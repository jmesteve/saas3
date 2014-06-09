import logging
import threading
import openerp

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileCreatedEvent
from watchdog.events import FileModifiedEvent

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# AutoReload watcher
#----------------------------------------------------------

class AutoReloadWatchdog(object):
    def __init__(self, server):
        self.server = server
        self.files = {}
        self.modules = {}
        class EventHandler(FileSystemEventHandler):
            def __init__(self, autoreload):
                self.autoreload = autoreload
            
            def process(self):
                l = self.autoreload.files.keys()
                self.autoreload.files.clear()
                self.autoreload.process_data(l)
                self.autoreload.process_python(l)
            
            def on_created(self, event):
                if isinstance(event, FileCreatedEvent):
                    _logger.debug('File created: %s', event.src_path)
                    self.autoreload.files[event.src_path] = 1
                    self.process()
            
            def on_modified(self, event):
                if isinstance(event, FileModifiedEvent):
                    _logger.debug('File modified: %s', event.src_path)
                    self.autoreload.files[event.src_path] = 1
                    self.process()

        #self.wm = pyinotify.WatchManager()
        self.handler = EventHandler(self)
        self.observer = Observer()
        #self.notifier = pyinotify.Notifier(self.wm, self.handler, timeout=0)
        #mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE  # IN_MOVED_FROM, IN_MOVED_TO ?
        for path in openerp.tools.config.options["addons_path"].split(','):
            _logger.info('Watching addons folder %s', path)
            #self.wm.add_watch(path, mask, rec=True)
            self.observer.schedule(self.handler, path=path, recursive=True)

    def process_data(self, files):
        xml_files = [i for i in files if i.endswith('.xml')]
        addons_path = openerp.tools.config.options["addons_path"].split(',')
        for i in xml_files:
            for path in addons_path:
                if i.startswith(path):
                    # find out which addons path the file belongs to
                    # and extract it's module name
                    right = i[len(path) + 1:].split('/')
                    if len(right) < 2:
                        continue
                    module = right[0]
                    self.modules[module]=1
        if self.modules:
            _logger.info('autoreload: xml change detected, autoreload activated')
            openerp.service.server.restart()

    def process_python(self, files):
        # process python changes
        py_files = [i for i in files if i.endswith('.py')]
        py_errors = []
        # TODO keep python errors until they are ok
        if py_files:
            for i in py_files:
                try:
                    source = open(i, 'rb').read() + '\n'
                    compile(source, i, 'exec')
                except SyntaxError:
                    py_errors.append(i)
            if py_errors:
                _logger.info('autoreload: python code change detected, errors found')
                for i in py_errors:
                    _logger.info('autoreload: SyntaxError %s',i)
            else:
                _logger.info('autoreload: python code updated, autoreload activated')
                openerp.service.server.restart()

    def check_thread(self):
        # Check if some files have been touched in the addons path.
        # If true, check if the touched file belongs to an installed module
        # in any of the database used in the registry manager.
        self.observer.run()

    def run(self):
        t = threading.Thread(target=self.check_thread)
        t.setDaemon(True)
        t.start()
        _logger.info('AutoReload watcher running')