from mulgrids import *
import string

def quick_enthalpy(t_or_p,ph='liq'):
    """ Return enthalpy J/kg ('liq', 'vap', or 'dif') of water at specified 
        temperature (<=500.0 in degC) or pressu (>500.0 in Pa) """
    import t2thermo
    def enth(t,p,f):
        d,u = f(t,p)
        return u + p/d
    def hlhs(t,p):
        return enth(t,p,t2thermo.cowat), enth(t,p,t2thermo.supst)
    def sat_tp(t_or_p):
        if t_or_p > 500.0:
            return t2thermo.tsat(t_or_p), t_or_p
        else:
            return t_or_p, t2thermo.sat(t_or_p)
    (hl,hs) = hlhs(*sat_tp(t_or_p))
    # xxxx
    return {'liq': hl,'vap': hs,'dif': hs-hl}[ph]

class RelativePermeability:
    """ Class to calculate linear relative permeability, this is used in
        TOUGH2 for the linear relative permeability model.  The class has a
        single method, which takes the saturation and returns the relative
        permeability. """
    def __init__(self, wj_object=None):
        if wj_object is None:
            wj_object = {
                "type": "linear",
                "liquid": [0.0, 1.0],
                "vapour": [0.0, 1.0]
            }
        self.setting = wj_object
        self.func = {
            "linear": self.linear,
        }

    def calc(self, vapour_saturation):
        """ return (kr_liquid, kr_vapour) """
        return self.func[self.setting['type']](vapour_saturation)

    def linear(self, vapour_saturation):
        liq_limits = self.setting['liquid']
        vap_limits = self.setting['vapour']
        liquid_saturation = 1.0 - vapour_saturation
        kr_liq = np.interp(liquid_saturation, liq_limits, [0., 1.], left=0.0, right=1.0)
        kr_vap = np.interp(vapour_saturation, vap_limits, [0., 1.], left=0.0, right=1.0)
        return kr_liq, kr_vap

def flowing_enthalpy(lst, wj, block):
    """ calculate flowing enthalpy of a given block if producing from waiwera h5

    NOTE use values from waiwera h5 at current time
    """
    phases = ['liquid', 'vapour']
    rp = RelativePermeability(wj['rock']['relative_permeability'])
    vapour_saturation = lst.element[block][f'fluid_vapour_saturation']
    rel_perm = rp.calc(vapour_saturation)
    fluid = lst.element[block]
    # mobility
    mobility, sum_mobility = {}, 0.0
    for iph, phase in enumerate(phases):
        density = fluid[f'fluid_{phase}_density']
        viscosity = fluid[f'fluid_{phase}_viscosity']
        if viscosity == 0.0:
            mobility[phase] = 0.0
        else:
            mobility[phase] = rel_perm[iph] * density / viscosity
        sum_mobility += mobility[phase]
    # flow fraction
    flow_frac = {}
    for phase in phases:
        flow_frac[phase] = mobility[phase] / sum_mobility
    # enthalpy
    enthalpy = 0.0
    for phase in phases:
        enthalpy += flow_frac[phase] * fluid[f'fluid_{phase}_specific_enthalpy']
    # breakpoint()
    return enthalpy

def bottomhole_pressure(depth, temperature=20.0, whp=1.0e5, division=100, 
                        min_depth_interval=10.0):
    """ Calculate the pressure at the bottom of a well, given the wellhead
        pressure (whp) in pascal, temperature in degC, and division in m. The
        pressure is calculated as: pressure = whp + rho * G * depth where rho is
        the density of water at the given temperature, G is the gravitational
        acceleration (9.81 m/s^2), and depth is the depth of the well divided by
        division.

        What tis code does is then divide the depth into inv=tervals.  Then the
        pressure is accumulated, this allows the density calculation to use the
        actual pressure at the depth.  For liquid water, it is quite
        incompressible, so the result won't be that different to the easy
        rho*G*depth method.        
    """
    import t2thermo
    # divide well depth to intervals, use larger of the min interval and division
    interval = max(min_depth_interval, depth/float(division))
    d = 0.0
    pressure = whp
    while d < depth:
        rho, u = t2thermo.cowat(temperature, pressure)
        pressure += rho * 9.81 * interval
        d += interval
    rho, u = t2thermo.cowat(temperature, pressure)
    pressure += rho * 9.81 * (depth - d)
    return pressure

def block_depth(block, geo):
    """ Return the depth of a block in a geo object, this is the depth of the
        centre of the block.  This also work for Waiwera cell if block is an
        integer number.
    """
    if isinstance(block, int):
        block = geo.block_name_list(block + geo.num_atmosphere_blocks)
    lay, col = geo.layer_name(block), geo.column_name(block)
    return geo.column[col].surface - geo.block_centre(lay, col)[2]

def xyz2fit(fn):
    data = np.fromfile(fn,sep=" ")
    nrow = np.size(data) / 3
    data= data.reshape(nrow,3)
    return data

def find_all_cols_below(geo,level,surfer_file=None):
    if surfer_file is not None: outfile = file(surfer_file,'w')
    cols = []
    for col in geo.columnlist:
        surf = col.surface
        if surf < level:
            #print(col.name, str(surf))
            cols.append([col.centre[0], col.centre[1], surf, col.name])
            if surfer_file is not None: outfile.write(
                str(col.centre[0])+' '+str(col.centre[1])+' '+str(surf)+' '+
                col.name + '\n')
    if surfer_file is not None:
        outfile.close()
        print(' -- file: ', surfer_file, ' is written.')

def t2_strict_name(n):
    """ convert any name into the common TOUGH style 5 character name """
    import string
    def make_number(c):
        """ change a character into a single number, mostly 'A' or 'a' will 
            become a '1' """
        if len(c.strip()) == 0: return ' '
        d = c.lower().strip()[:1]
        i = string.ascii_lowercase.find(d)+1
        if i == 0: return ' '
        else: return str(i%10)
    newn = list(n.strip())
    if len(newn) <= 3:
        return "".join(newn).strip()[:5].ljust(5)
    for i in range(3,len(newn)):
        if newn[i] not in '0123456789':
            newn[i] = make_number(newn[i])
    return "".join(newn).strip()[:5].ljust(5)

def is_leap_year(y):
    if   int(y)%400 == 0: return True
    elif int(y)%100 == 0: return False
    elif int(y)%4   == 0: return True
    else:                 return False

def days_in_month(month, leap_year=False):
    if leap_year:
        d_month = [  31 , 29 , 31 , 30 , 31 , 30 , 31 , 31 , 30 , 31 , 30 , 31  ]
    else:
        d_month = [  31 , 28 , 31 , 30 , 31 , 30 , 31 , 31 , 30 , 31 , 30 , 31  ]
    return d_month[month - 1]

def date2str(d,m,y):
    ds, ms, ys = str(d), str(m), str(y)
    while len(ds) < 2: ds = '0'+ds
    while len(ms) < 2: ms = '0'+ms
    while len(ys) < 4: ys = '0'+ys
    return ds+'/'+ms+'/'+ys

def date2num(enddate):
            
    d,m,y = enddate.split('/')
    months    = [ '01','02','03','04','05','06','07','08','09','10','11','12' ]
    d_month   = [  31 , 28 , 31 , 30 , 31 , 30 , 31 , 31 , 30 , 31 , 30 , 31  ]
    d_month_l = [  31 , 29 , 31 , 30 , 31 , 30 , 31 , 31 , 30 , 31 , 30 , 31  ]
    acum_ds   = [sum(d_month[:i]) for i in range(12)]
    acum_ds_l = [sum(d_month[:i]) for i in range(12)]
    ad_m   = dict(zip(months, acum_ds)) # accumulated days before this month
    ad_m_l = dict(zip(months, acum_ds_l)) # accumulated days before this month
    ds_m   = dict(zip(months, d_month)) # maximum days in this month
    ds_m_l = dict(zip(months, d_month_l)) # maximum days in this month
    # check and process d and m, this depends on data
    if m not in months:
        print(' Error, unable to convert ', enddate, ' to numeric format. check month.')
        sys.exit()
    if is_leap_year:
        if int(d) not in range(1,ds_m_l[m]+1):
            print(' Error, unable to convert ', enddate, ' to numeric format. check day.')
            sys.exit()
        num = float(y) + ((float(d) + float(ad_m_l[m]))/float(sum(d_month_l)))
    else:
        if int(d) not in range(1,ds_m[m]+1):
            print(' Error, unable to convert ', enddate, ' to numeric format. check day.')
            sys.exit()
        num = float(y) + ((float(d) + float(ad_m[m]))/float(sum(d_month)))
    return num


def identifier(x, chars='abcdefghijklmnopqrstuvwxyz', width=5):
    """ creates a character-based unique identifier from a given integer,
        both chars and width are customisable, output is space filled and
        right aligned """
    output = []
    base = len(chars)
    while x:
        output.append(chars[x % base])
        x /= base
    final = ''.join(reversed(output))
    if len(final) > width:
        raise Exception('identifier() failed, not enough width.')
    return ('%' + str(width) + 's') % final

