from yta_editor.transformations.effects.abstract import EffectParams
from yta_editor.transformations.effects.video import VideoEffect
from yta_editor.transformations.time_function import TimeFunction, ConstantTimeFunction
from yta_editor_nodes.processor import BrightnessNodeProcessor
from dataclasses import dataclass


# TODO: We need to define all the specific effect
# params to be able to build them properly missing
# no fields
@dataclass
class BrightnessVideoEffectParams(EffectParams):
    """
    The parameters to use when applying the effect
    that changes the brightness for a specific `t`
    time moment.

    This will be returned by the effect when
    calculated, for a specific `t` time moment.
    """

    def __init__(
        self,
        brightness: float
    ):
        self.brightness: float = brightness
        """
        The value to apply as brightness.
        """
        

class BrightnessVideoEffect(VideoEffect):
    """
    The effect that will change the brightness of the
    element according to the provided conditions.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        brightness: TimeFunction = ConstantTimeFunction(2.0)
    ):
        self.do_use_gpu: bool = do_use_gpu
        """
        Flag to indicate if using GPU or not.
        """
        self.brightness: TimeFunction = brightness
        """
        The `TimeFunction` that defines the value that should
        be applied for the specific `t` time moment requested.
        """

    def _get_params_at(
        self,
        t: float
    ) -> BrightnessVideoEffectParams:
        """
        *For internal use only*

        Get the parameters that must be applied at the given
        `t` time moment.
        """
        return BrightnessVideoEffectParams(self.brightness.get_value_at(t))

    def apply(
        self,
        # TODO: Set the type
        frame,
        t: float,
    ):
        """
        Apply the effect to the given `frame` at the `t` time
        moment provided.
        """
        params = self._get_params_at(t)

        if params.brightness == 1.0:
            return frame
        
        import numpy as np

        frame_processed = frame.astype(np.float32) / 255.0
        frame_processed *= params.brightness

        # TODO: Something is going wrong with the effect
        
        # frame_processed = BrightnessNodeProcessor(
        #     do_use_gpu = self.do_use_gpu,
        #     factor = params.brightness
        # ).process(
        #     input = frame_processed
        # )

        frame_processed = np.clip(frame_processed * 255.0, 0, 255).astype(np.uint8)

        # TODO: Do I need to parse/reformat the frame (?)
        return frame_processed