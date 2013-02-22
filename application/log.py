"""
    log.py
    Logging code for ScalyMUCK
    Copyright (c) 2012 Liukcairo
"""

class Log:
    _target_file = None
    _echo = False
    def set_target(self, target_file, do_echo):
        file_handle = None
        try:
            file_handle = open(target_file, 'w')

            text = 'ScalyMUCK Copyright (c) 2013 Liukcairo\n\n'
            if (do_echo):
                print(text)
            file_handle.write(text)
        except:
            return False
        file_handle.close()
        self._target_file = target_file
        self._echo = do_echo
        return True

    def write(self, data):
        if (_target_file is None):
            return False
        file_handle = open(_target_file, 'a')
        file_handle.write(data + '\n')
        file_handle.close()

        if (self._echo is True):
            print(data)

        return True

    def get_target(self):
        return self._target_file

    def is_ready(self):
        if (self._target_file is None):
            return False
        else:
            return True

    def set_echo(self, status):
        self._echo = status