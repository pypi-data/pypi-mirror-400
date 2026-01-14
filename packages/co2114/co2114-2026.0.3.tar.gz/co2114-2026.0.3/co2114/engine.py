"""ENGINE.PY
This contains the code for the base engine
"""
import warnings
import time
from datetime import datetime
from collections.abc import Iterable, Callable
from typing import override

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pygame

if __name__ == "__main__":  # being run as script
    from co2114.util import colours, fonts
    COLOR_BLACK, COLOR_WHITE = colours.COLOR_BLACK, colours.COLOR_WHITE
else:
    from .util.colours import COLOR_BLACK, COLOR_WHITE
    from .util import fonts
    
TEXT_FONT = fonts._get_text_font_unsafe()  # default text font

## GLOBALS
DEFAULT_FPS:int = 30  # Render frames per second
DEFAULT_LPS:int = 2   # Environment steps per second

class BaseEngine:
    """ Base Engine Class 
            
            Provides basic PyGame setup and event loop
    """
    size = width, height = 600, 400  # default window size

    def __init__(self) -> None:
        """ Initialise Base Engine """
        print(f"Creating instance of {self.name} ({self.__class__.__name__})")

        pygame.init() # initialise pygame

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(f"{self.name} (co2114)")
        self._font = pygame.font.SysFont(TEXT_FONT, 28)  # default system font
        self._running:bool = True


    @property
    def name(self) -> str:
        """ Get engine name """
        return self.__class__.__name__
    
    @property
    def isrunning(self) -> bool:
        """ Check if engine is running """
        return self._running
    

    def on_event(self, event:pygame.event.Event) -> None:
        """ Event handler """
        if event.type == pygame.QUIT:
            self._running = False


    def cleanup(self) -> None:
        """ Cleanup engine on exit """
        print(f"Quiting {self.name}")
        pygame.quit()


    def _run(self, *render_sequence:Callable) -> None:
        """ Main event loop 
        
        :param *render_sequence: sequence of functions to call each loop
        """
        while self.isrunning:
            for event in pygame.event.get():
                self.on_event(event)  # handle events
            for fcn in render_sequence:  # call each function
                fcn()
        self.cleanup()  # cleanup on exit


class Engine(BaseEngine):
    """Engine Class
        Provides basic framerate and looprate control"""
    
    def __init__(self,
                 fps:int = DEFAULT_FPS,
                 lps:int = DEFAULT_LPS,
                 dims:tuple[int,int]|None = None) -> None:
        """ Initialise Engine
        
        :param fps: frames per second (render rate)
        :param lps: loops per second (process rate)
        :param dims: optional dimensions tuple (width, height)
        """
        # set dimensions if provided
        if dims and isinstance(dims, Iterable) and len(dims)==2:
            self.size = self.width, self.height = dims
    
        super().__init__()  # initialise base engine

        self._framerate:int = fps if isinstance(fps, int) else DEFAULT_FPS
        self._looprate:int = lps if isinstance(lps, int) else DEFAULT_LPS
        self._t0, self._l0 = time.time(), time.time()  # timing count


    def _update(self) -> None:
        """ Processing loop internals """
        # frame limiter
        if self._framerate is None or not isinstance(self._framerate, int):
            self._framerate = DEFAULT_FPS  # corrective measures
        mspf = (1000/self._framerate)  # ms per frame
        if (time.time() - self._t0) < mspf:  # if faster than framerate
            time.sleep((mspf - (time.time()-self._t0))/1000)  # sleep
        self._t0 = time.time()  # update timer

        # main render loop
        if self._looprate is None or not isinstance(self._looprate, int):
            self._looprate = DEFAULT_LPS  # corrective measures
        spf = 1/self._looprate  # s per frame
        if(time.time() - self._l0) > spf:  # if enough time passed
            self._l0 = time.time()  # update timer
            self.update()  # run main process update


    def _render(self) -> None:
        """ Render loop internals """
        self.screen.fill(COLOR_BLACK)  # write black to buffer
        self.render()  # run main render loop
        pygame.display.flip()  # flip buffer


    def update(self) -> None:
        """ Main process loop, needs override """
        raise NotImplementedError

    def render(self) -> None:
        """ Main render loop, needs override """
        raise NotImplementedError
    
    
    def run(self) -> None:
        """ Run the engine """
        super()._run(self._update, self._render)


class App(Engine):
    """ Base App Class

            Provides default name and run method for GUI apps
    """
    def __init__(self, *args, name:str | None = None, **kwargs) -> None:
        """ Initialise App
        
        :param    *args: positional arguments for Engine
        :param     name: optional name for the app
        :param **kwargs: keyword arguments for Engine
        """
        if name is not None: self._name = name  # set name if provided
        super().__init__(*args, **kwargs)  # initialise engine

    
    @classmethod
    def run_default(cls) -> None:
        """ Run the app with default parameters """
        app = cls()
        app.run()


    @property
    def name(self) -> str:
        """ Get app name """
        return self._name if hasattr(self, "_name") else super().name


class EmptyApp(App):
    """ Dummy Class for testing """
    pass

#######################
class ClockApp(App):
    """ Example PyGame App """
    
    # size = width, height = 600, 400  # uncomment to override

    def __init__(self) -> None:
        """ Initialise Clock App """
        super().__init__(fps=60, lps=60)  # initialise app
        self._font = pygame.font.SysFont(TEXT_FONT, 128)  # override font
        self.t = datetime.now()  # current time

    # @override
    def update(self) -> None:
        """ Main process loop

                Gets current system time
        """
        self.t = datetime.now()  # get current time
    
    # @override
    def render(self) -> None:
        """ Main render loop 

                Writes time to screen
        """
        # render time string
        renderTime = self._font.render(
            self.t.strftime("%H:%M:%S.%f")[:-5],
            True,
            COLOR_WHITE)
        rect = renderTime.get_rect()
        # blit to screen centered
        self.screen.blit(
            renderTime, 
            (self.width//2 - rect.width//2, 
             self.height//2 - rect.height//2))


####################################
if __name__ == "__main__":
    """ Run ClockApp if engine.py is run as script """
    print("Running engine.py as script.")
    ClockApp.run_default()