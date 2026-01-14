
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.io
import java.lang
import java.util
import jneqsim.neqsim.process.advisory
import jneqsim.neqsim.process.alarm
import jneqsim.neqsim.process.calibration
import jneqsim.neqsim.process.conditionmonitor
import jneqsim.neqsim.process.controllerdevice
import jneqsim.neqsim.process.costestimation
import jneqsim.neqsim.process.equipment
import jneqsim.neqsim.process.fielddevelopment
import jneqsim.neqsim.process.integration
import jneqsim.neqsim.process.logic
import jneqsim.neqsim.process.measurementdevice
import jneqsim.neqsim.process.mechanicaldesign
import jneqsim.neqsim.process.ml
import jneqsim.neqsim.process.mpc
import jneqsim.neqsim.process.processmodel
import jneqsim.neqsim.process.safety
import jneqsim.neqsim.process.streaming
import jneqsim.neqsim.process.sustainability
import jneqsim.neqsim.process.util
import jneqsim.neqsim.util
import typing



class SimulationInterface(jneqsim.neqsim.util.NamedInterface, java.lang.Runnable, java.io.Serializable):
    def getCalculateSteadyState(self) -> bool: ...
    def getCalculationIdentifier(self) -> java.util.UUID: ...
    def getReport_json(self) -> java.lang.String: ...
    def getTime(self) -> float: ...
    def increaseTime(self, double: float) -> None: ...
    def isRunInSteps(self) -> bool: ...
    @typing.overload
    def run(self, uUID: java.util.UUID) -> None: ...
    @typing.overload
    def run(self) -> None: ...
    @typing.overload
    def runTransient(self, double: float) -> None: ...
    @typing.overload
    def runTransient(self, double: float, uUID: java.util.UUID) -> None: ...
    @typing.overload
    def run_step(self, uUID: java.util.UUID) -> None: ...
    @typing.overload
    def run_step(self) -> None: ...
    def setCalculateSteadyState(self, boolean: bool) -> None: ...
    def setCalculationIdentifier(self, uUID: java.util.UUID) -> None: ...
    def setRunInSteps(self, boolean: bool) -> None: ...
    def setTime(self, double: float) -> None: ...
    def solved(self) -> bool: ...

class SimulationBaseClass(jneqsim.neqsim.util.NamedBaseClass, SimulationInterface):
    def __init__(self, string: typing.Union[java.lang.String, str]): ...
    def getCalculateSteadyState(self) -> bool: ...
    def getCalculationIdentifier(self) -> java.util.UUID: ...
    def getTime(self) -> float: ...
    def increaseTime(self, double: float) -> None: ...
    def isRunInSteps(self) -> bool: ...
    def setCalculateSteadyState(self, boolean: bool) -> None: ...
    def setCalculationIdentifier(self, uUID: java.util.UUID) -> None: ...
    def setRunInSteps(self, boolean: bool) -> None: ...
    def setTime(self, double: float) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process")``.

    SimulationBaseClass: typing.Type[SimulationBaseClass]
    SimulationInterface: typing.Type[SimulationInterface]
    advisory: jneqsim.neqsim.process.advisory.__module_protocol__
    alarm: jneqsim.neqsim.process.alarm.__module_protocol__
    calibration: jneqsim.neqsim.process.calibration.__module_protocol__
    conditionmonitor: jneqsim.neqsim.process.conditionmonitor.__module_protocol__
    controllerdevice: jneqsim.neqsim.process.controllerdevice.__module_protocol__
    costestimation: jneqsim.neqsim.process.costestimation.__module_protocol__
    equipment: jneqsim.neqsim.process.equipment.__module_protocol__
    fielddevelopment: jneqsim.neqsim.process.fielddevelopment.__module_protocol__
    integration: jneqsim.neqsim.process.integration.__module_protocol__
    logic: jneqsim.neqsim.process.logic.__module_protocol__
    measurementdevice: jneqsim.neqsim.process.measurementdevice.__module_protocol__
    mechanicaldesign: jneqsim.neqsim.process.mechanicaldesign.__module_protocol__
    ml: jneqsim.neqsim.process.ml.__module_protocol__
    mpc: jneqsim.neqsim.process.mpc.__module_protocol__
    processmodel: jneqsim.neqsim.process.processmodel.__module_protocol__
    safety: jneqsim.neqsim.process.safety.__module_protocol__
    streaming: jneqsim.neqsim.process.streaming.__module_protocol__
    sustainability: jneqsim.neqsim.process.sustainability.__module_protocol__
    util: jneqsim.neqsim.process.util.__module_protocol__
