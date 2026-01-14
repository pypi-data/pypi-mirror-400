""" CONFIG 
"""


class Singleton(object):
    __single = None # the one, true Singleton

    def __new__(classtype, *args, **kwargs):
        # Check to see if a __single exists already for this class
        # Compare class types instead of just looking for None so
        # that subclasses will create their own __single objects
        if classtype != type(classtype.__single):
            classtype.__single = object.__new__(classtype, *args, **kwargs)
        return classtype.__single

        
#class config(Singleton):
class config(object):
    def __init__(self,filename=''):
        self.empty()
        if filename: self.read_from_file(filename)
    def empty(self):
        self._config_entries = {}
        
    def read_from_file(self,filename=None):
        """ read config from a whole file, until [END], if filename
            is not given, user will be prompted for a filename."""
        if filename==None:
            filename=raw_input(' Configuration file (.cfg) name? ')
        print(" Reading file", filename.strip(), "for configurations...")
        
        cfgfile=open(filename)
        self._read(cfgfile)    
        cfgfile.close()
        
    def read_from_file_section(self,file_with_cfg):
        """ only read config entries from the current location, 
            file_with_cfg should be already opened, and reading will
            be terminated once [END] is reached, the calling program 
            can continue read the rest of the file. """
        self._read(file_with_cfg)
        
    def _read(self,cfgfile):
        finished=False
        while not finished:
            line = cfgfile.readline()
            if line:
                if line.strip()=='': continue
                if line.strip()[0]=='!': continue
                if line.strip()[0]=='#': continue
                if line.strip()[0]=='[':
                    ikeyend=line.find(']')
                    keyword=line[1:ikeyend]
                    if keyword=='END': break
                    self._config_entries[keyword]=[]
                else: 
                    self._config_entries[keyword].append(line.rstrip('\n\r'))
            else: finished = True
    def add_value(self,keyword,value):
        """ add value manually, value can be a single value, or a list, 
            or whatever object, as long as you know what it is when you
            get it out, if keyword exist, the value wil be appended """
        if keyword in self._config_entries:
            try:
                self._config_entries[keyword].append(value)
            except:
                self._config_entries[keyword] = [self._config_entries[keyword], value]
        else:
            self._config_entries[keyword] = [value]
        
    def get_value(self,keyword):
        if len(self._config_entries[keyword]) == 0:
            return ''
        else:
            return self._config_entries[keyword][0]
        
    def get_list(self,keyword):
        return self._config_entries[keyword]

    def check_optional(self,keyword):
        return keyword in self._config_entries.keys()

