import os
import sys
import ctypes
import numpy as np
import pathlib
from importlib.metadata import version
from datetime import datetime


if sys.platform == "win32":
    libfile = "libzrod.cp313-win_amd64.pyd"
elif sys.platform == "darwin":
    libfile = "libzrod.cpython-313-darwin.so"
else:
    libfile = "libzrod.cpython-312-x86_64-linux-gnu.so"
    if(os.path.isfile(pathlib.Path(__file__).parent / libfile) == False): libfile = "libzrod.cpython-38-x86_64-linux-gnu.so"
#endif

libfile = pathlib.Path(__file__).parent / libfile
libzrod = ctypes.CDLL(str(libfile))


def testme():
    print("libzrod testme")
#end testme()


class TaperBase_t(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_char * 32),
        ('L', ctypes.c_double),
        ('D', ctypes.c_double),
        ('W', ctypes.c_double),
        ('T', ctypes.c_double),
        ('E', ctypes.c_double),
        ('R', ctypes.c_double)
    ]
#end TaperBase_t
class TubingBase_t(ctypes.Structure):
    _fields_ = [
        ('L', ctypes.c_double),
        ('innerDiameter', ctypes.c_double),
        ('outerDiameter', ctypes.c_double),
        ('weight', ctypes.c_double),
        ('W', ctypes.c_double),
        ('T', ctypes.c_double),
        ('E', ctypes.c_double),
        ('R', ctypes.c_double)
    ]
#end TubingBase_t

class CasingBase_t(ctypes.Structure):
    _fields_ = [
        ('L', ctypes.c_double),              # Length of casing section
        ('innerDiameter', ctypes.c_double),  # Inner diameter
        ('outerDiameter', ctypes.c_double),  # Outer diameter
        ('weight', ctypes.c_double),         # Weight per foot (lb/ft)
        ('casingType', ctypes.c_char * 32),  # Casing type (Surface, Intermediate, Production, Liner)
        ('casingGrade', ctypes.c_char * 32)  # API casing grade (J-55, K-55, L-80, N-80, P-110, etc.)
    ]
#end CasingBase_t

class WaveResult_t(ctypes.Structure):
    _fields_ = [
        ('Rwa', ctypes.c_double),
        ('Rwf', ctypes.c_double),
        ('RTT', ctypes.c_double),
        ('AvgRodWaveVelocity', ctypes.c_double),
        ('FoSKr', ctypes.c_double),
        ('NNo', ctypes.c_double),
        ('SKr', ctypes.c_double),
        ('SL', ctypes.c_double),
        ('Kr', ctypes.c_double),
        ('Kt', ctypes.c_double),
        ('KtUnanchored', ctypes.c_double),
        ('BblPerDay100', ctypes.c_double),
        ('GallonsPerStroke100', ctypes.c_double),
        ('PumpStrokeGross', ctypes.c_double),
        ('PumpStrokeNet', ctypes.c_double),
        ('PumpStrokeMin', ctypes.c_double),
        ('PumpStrokeMax', ctypes.c_double),
        ('slippage', ctypes.c_double),
        #//WaveRESULT_XXX
    ]
#end WaveResult_t

'''
class PumpValvePointInfo_t(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_int),
        ('valvestate', ctypes.c_int),
    ]
#end PumpValvePointInfo_t
'''

class WaveResults_t(ctypes.Structure):
    _fields_ = [
        ('LastExecutionTimeMs', ctypes.c_int),
        ('diag', WaveResult_t),
        ('pred', WaveResult_t),

        #TODO: this might get moved/renamed
        ('predPumpTvClosedIndex', ctypes.c_int),
        ('predPumpSvOpenedIndex', ctypes.c_int),
        ('predPumpSvClosedIndex', ctypes.c_int),
        ('predPumpTvOpenedIndex', ctypes.c_int),

        ('predCalcdFo', ctypes.c_double), #this is the Fo from the plunger, pressures and FL. The target Fo in WaveParams_t can be set manually.
        ('predPumpIntakePressure', ctypes.c_double),
        ('predPumpDischargePressure', ctypes.c_double),
    ]
#end WaveResults_t

class WaveParams_t(ctypes.Structure):
    _fields_ = [
        ('WellDepth', ctypes.c_double),

        ('diagSpm', ctypes.c_double),
        ('predSpm', ctypes.c_double),

        ('diagDampUp', ctypes.c_double),
        ('diagDampDn', ctypes.c_double),
        ('predDampUp', ctypes.c_double),
        ('predDampDn', ctypes.c_double),

        ('diagFluidSG', ctypes.c_double),
        ('predFluidSG', ctypes.c_double),

        ('diagFluidViscosity', ctypes.c_double),
        ('predFluidViscosity', ctypes.c_double),

        ('diagPumpPlungerDiameter', ctypes.c_double),
        ('diagPumpPlungerLength', ctypes.c_double),
        ('diagPumpPlungerClearance', ctypes.c_double),

        ('predPumpPlungerDiameter', ctypes.c_double),
        ('predPumpPlungerLength', ctypes.c_double),
        ('predPumpPlungerClearance', ctypes.c_double),

        ('diagTubingPressure', ctypes.c_double),
        ('diagCasingPressure', ctypes.c_double),
        ('predTubingPressure', ctypes.c_double),
        ('predCasingPressure', ctypes.c_double),

        ('diagFluidLevel', ctypes.c_double),
        ('predFluidLevel', ctypes.c_double),

        ('diagPumpDepth', ctypes.c_double),
        ('predPumpDepth', ctypes.c_double),

        ('diagAnchorDepth', ctypes.c_double),
        ('predAnchorDepth', ctypes.c_double),

        ('predFo', ctypes.c_double), #This is the target Fo. Ideally set by CalculateFo(), but can be set manually. If manually set, see predCalcdFo in WaveResults_t.
        ('predFillage', ctypes.c_double),
        ('predCompression', ctypes.c_double),

        #('predCyclesToRun', ctypes.c_int),
        #('predCyclesToOutput', ctypes.c_int),

        ('usePumpingUnitForPosition', ctypes.c_bool),

        #//WavePARAM_XXX
    ]
#end WaveParams_t

class WaveParamsReadOnly_t(ctypes.Structure):
    _fields_ = [
        ('diagMeasM', ctypes.c_int),
        ('diagUpscM', ctypes.c_int),
        ('predM', ctypes.c_int),
        #('diagMeasDX', ctypes.c_double),
        #('diagUpscDX', ctypes.c_double),
        #('predDX', ctypes.c_double),
        ('diagMeasDT', ctypes.c_double),
        ('diagUpscDT', ctypes.c_double),
        ('predDT', ctypes.c_double),
        ('diagMeasPointCount', ctypes.c_int),
        ('diagUpscPointCount', ctypes.c_int),
        ('predPointCount', ctypes.c_int),
        ('diagStrokePeriod', ctypes.c_double),
        ('predStrokePeriod', ctypes.c_double),
        ('diagBuoyancyForce', ctypes.c_double),
        ('predBuoyancyForce', ctypes.c_double),
    ]
#end WaveParamsReadOnly_t

# Prediction algorithm type enumeration
PRED_ALGORITHM_STANDARD = 0
PRED_ALGORITHM_OLD = 1
PRED_ALGORITHM_EXPERIMENTAL = 2

#Default settings should be fine for most cases (i.e. you shouldnt need this except for advanced useage. Also, be ware this may change substantially between releases.)
class WaveSettings_t(ctypes.Structure):
    _fields_ = [
        ('predAlgorithmType', ctypes.c_int),  # PRED_ALGORITHM_* constant
        #('predLimitPointCount', ctypes.c_int),
        ('predNodesPerSection', ctypes.c_int),
        ('includeBuoyancy', ctypes.c_bool),
        ('zeroPumpPosition', ctypes.c_bool),
        ('extraParams', ctypes.c_int),
        ('skipCalcMeas', ctypes.c_bool),
        ('skipCalcUpsc', ctypes.c_bool),
        ('skipCalcPred', ctypes.c_bool),
    ]
#end WaveSettings_t

class PuApi_t(ctypes.Structure):
    _fields_ = [
        ('Rotate', ctypes.c_int),
        ('A', ctypes.c_double),
        ('P', ctypes.c_double),
        ('C', ctypes.c_double),
        ('I', ctypes.c_double),
        ('K', ctypes.c_double),
        ('R', ctypes.c_double),
        ('Torque', ctypes.c_double),
        ('Structure', ctypes.c_double),
        ('MaxStroke', ctypes.c_double),
        ('Type', ctypes.c_char),
        ('isDoubleReducer', ctypes.c_bool),
        ('CBE', ctypes.c_double),
        ('B', ctypes.c_double),
        ('Tau', ctypes.c_double),
        ('Cyl', ctypes.c_double),
        ('CylFactor', ctypes.c_double),
        ('S', ctypes.c_double),
    ]
#end PuApi_t

class PuInfo_t(ctypes.Structure):
    _fields_ = [
        ('api', PuApi_t),
        #TODO: more info about this unit like the Database key
    ]
#end PuInfo_t

class DeviationSurveyPoint_t(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_int),
        ('md', ctypes.c_double),
        ('inc', ctypes.c_double),
        ('azi', ctypes.c_double),
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
        ('z', ctypes.c_double),
        ('dls', ctypes.c_double)
    ]
#end DeviationSurveyPoint_t

class DesignInfo_t(ctypes.Structure):
    _fields_ = [
        ('designId', ctypes.c_char * 84),
        ('ts', ctypes.c_char * 24),
        ('designTitle', ctypes.c_char * 64),
        ('shortcomment', ctypes.c_char * 128),
    ]
#end DesignInfo_t
class DesignInfo():
    def __init__(self, designId, ts, designTitle):
        self.designId = designId
        self.ts = ts
        self.designTitle = designTitle
        try:
            # Parse timestamp format "2025-08-23T21:32:44.588"
            self.timestamp = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            self.timestamp = None
    #end __init__
#end DesignInfo

clogfunc = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
libzrod.SetLoggingCallback.argtypes = [clogfunc]

zrodHandle = ctypes.POINTER(ctypes.c_char)
c_int_array =    np.ctypeslib.ndpointer(dtype=np.int32,   ndim=1, flags='C_CONTIGUOUS')
c_double_array = np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS')

libzrod.CreateZrodObj.restype = zrodHandle
libzrod.DeleteZrodObj.argtypes = [zrodHandle]
libzrod.PrintZrodObj.argtypes = [zrodHandle]
libzrod.GetZrodVersion.argtypes = [zrodHandle, c_int_array]
try:
    libzrod.DebugZrodObj.argtypes = [zrodHandle, ctypes.c_char_p]
except:
    pass
#end try

libzrod.Login.argtypes = [zrodHandle, ctypes.c_char_p, ctypes.c_char_p]
libzrod.Login.restype = ctypes.c_bool
libzrod.Logout.argtypes = [zrodHandle]
libzrod.Logout.restype = ctypes.c_bool

libzrod.Test.argtypes = [zrodHandle]

libzrod.SaveCurrentDesign.argtypes = [zrodHandle, ctypes.c_bool]
libzrod.SaveCurrentDesign.restype = ctypes.c_bool

libzrod.FetchDesigns.argtypes = [zrodHandle, ctypes.c_bool]
libzrod.FetchDesigns.restype = ctypes.c_int

libzrod.GetDesign.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.GetDesign.restype = ctypes.c_bool

libzrod.GetDesigns.argtypes = [zrodHandle, ctypes.POINTER(DesignInfo_t)]
libzrod.GetDesigns.restype = ctypes.c_bool

libzrod.DeleteDesign.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.DeleteDesign.restype = ctypes.c_bool

libzrod.runzrod.argtypes = [zrodHandle]

libzrod.RunDesign.argtypes = [zrodHandle]
libzrod.RunDesign.restype = ctypes.c_bool

libzrod.GetWaveResults.argtypes = [zrodHandle]
libzrod.GetWaveResults.restype = WaveResults_t

libzrod.GetWaveParamsReadOnly.argtypes = [zrodHandle]
libzrod.GetWaveParamsReadOnly.restype = WaveParamsReadOnly_t

libzrod.GetWaveParams.argtypes = [zrodHandle]
libzrod.GetWaveParams.restype = WaveParams_t
libzrod.SetWaveParams.argtypes = [zrodHandle, WaveParams_t]
libzrod.SetWaveParams.restype = ctypes.c_bool

libzrod.GetWaveSettings.argtypes = [zrodHandle]
libzrod.GetWaveSettings.restype = WaveSettings_t
libzrod.SetWaveSettings.argtypes = [zrodHandle, WaveSettings_t]
libzrod.SetWaveSettings.restype = ctypes.c_bool

libzrod.GetDeviationSurveyCount.argtypes = [zrodHandle]
libzrod.GetDeviationSurveyCount.restype = ctypes.c_int
libzrod.GetDeviationSurvey.argtypes = [zrodHandle, ctypes.c_void_p]
libzrod.GetDeviationSurvey.restype = ctypes.c_bool

#EXPORT bool SetDeviationSurvey(void * zrodptr, int count, double * md, double * inc, double * azi);
#EXPORT bool SetDeviationSurveyWithMIA(void * zrodptr, int count, double * mia);

libzrod.SetClientVersion.argtypes = [zrodHandle, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
libzrod.SetClientVersion.restype = ctypes.c_bool

libzrod.SetDesignTitle.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.SetDesignTitle.restype = ctypes.c_bool
libzrod.GetDesignTitle.argtypes = [zrodHandle]
libzrod.GetDesignTitle.restype = ctypes.c_char_p

libzrod.SetComment.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.SetComment.restype = ctypes.c_bool
libzrod.GetComment.argtypes = [zrodHandle]
libzrod.GetComment.restype = ctypes.c_char_p

#libzrod.SetDesignID.argtypes = [zrodHandle, ctypes.c_char_p] #not allowing setDesignID yet
#libzrod.SetDesignID.restype = ctypes.c_bool
libzrod.GetDesignID.argtypes = [zrodHandle]
libzrod.GetDesignID.restype = ctypes.c_char_p

libzrod.LoadDyn.argtypes = [zrodHandle, ctypes.c_double, c_double_array, c_double_array, ctypes.c_int]
libzrod.LoadDyn.restype = ctypes.c_bool
libzrod.LoadDynFromFileContents.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.LoadDynFromFileContents.restype = ctypes.c_bool
libzrod.LoadDynFromFile.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.LoadDynFromFile.restype = ctypes.c_bool

libzrod.WriteDesignFile.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.WriteDesignFile.restype = ctypes.c_bool
libzrod.WriteDesignFileWithTemplate.argtypes = [zrodHandle, ctypes.c_char_p, ctypes.c_char_p]
libzrod.WriteDesignFileWithTemplate.restype = ctypes.c_bool

libzrod.ParseDesignFileContents.argtypes = [zrodHandle, ctypes.c_char_p, ctypes.c_char]
libzrod.ParseDesignFileContents.restype = ctypes.c_bool
libzrod.ParseDesignFile.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.ParseDesignFile.restype = ctypes.c_bool

libzrod.GetMeasuredDynoPointCount.argtypes = [zrodHandle]
libzrod.GetMeasuredDynoPointCount.restype = ctypes.c_int
libzrod.GetMeasuredDyno.argtypes = [zrodHandle, c_double_array, c_double_array]
libzrod.GetMeasuredDyno.restype = ctypes.c_bool
libzrod.GetMeasuredPump.argtypes = [zrodHandle, c_double_array, c_double_array]
libzrod.GetMeasuredPump.restype = ctypes.c_bool
libzrod.GetMeasuredPumpColors.argtypes = [zrodHandle, c_int_array]
libzrod.GetMeasuredPumpColors.restype = ctypes.c_bool
libzrod.GetMeasuredPumpVelocity.argtypes = [zrodHandle, c_double_array]
libzrod.GetMeasuredPumpVelocity.restype = ctypes.c_bool
libzrod.GetMeasuredPumpVelocityNormalized.argtypes = [zrodHandle, c_double_array]
libzrod.GetMeasuredPumpVelocityNormalized.restype = ctypes.c_bool
libzrod.GetMeasuredPumpChamberPressure.argtypes = [zrodHandle, c_double_array]
libzrod.GetMeasuredPumpChamberPressure.restype = ctypes.c_bool
libzrod.GetMeasuredPumpChamberPressureNormalized.argtypes = [zrodHandle, c_double_array]
libzrod.GetMeasuredPumpChamberPressureNormalized.restype = ctypes.c_bool

libzrod.GetUpscaledDynoPointCount.argtypes = [zrodHandle]
libzrod.GetUpscaledDynoPointCount.restype = ctypes.c_int
libzrod.GetUpscaledDyno.argtypes = [zrodHandle, c_double_array, c_double_array]
libzrod.GetUpscaledDyno.restype = ctypes.c_bool
libzrod.GetUpscaledPump.argtypes = [zrodHandle, c_double_array, c_double_array]
libzrod.GetUpscaledPump.restype = ctypes.c_bool
libzrod.GetUpscaledPumpColors.argtypes = [zrodHandle, c_int_array]
libzrod.GetUpscaledPumpColors.restype = ctypes.c_bool
libzrod.GetUpscaledPumpVelocity.argtypes = [zrodHandle, c_double_array]
libzrod.GetUpscaledPumpVelocity.restype = ctypes.c_bool
libzrod.GetUpscaledPumpVelocityNormalized.argtypes = [zrodHandle, c_double_array]
libzrod.GetUpscaledPumpVelocityNormalized.restype = ctypes.c_bool
libzrod.GetUpscaledPumpChamberPressure.argtypes = [zrodHandle, c_double_array]
libzrod.GetUpscaledPumpChamberPressure.restype = ctypes.c_bool
libzrod.GetUpscaledPumpChamberPressureNormalized.argtypes = [zrodHandle, c_double_array]
libzrod.GetUpscaledPumpChamberPressureNormalized.restype = ctypes.c_bool

libzrod.GetPredDynoPointCount.argtypes = [zrodHandle]
libzrod.GetPredDynoPointCount.restype = ctypes.c_int
libzrod.GetPredDyno.argtypes = [zrodHandle, c_double_array, c_double_array]
libzrod.GetPredDyno.restype = ctypes.c_bool
libzrod.GetPredPump.argtypes = [zrodHandle, c_double_array, c_double_array]
libzrod.GetPredPump.restype = ctypes.c_bool
libzrod.GetPredPumpColors.argtypes = [zrodHandle, c_int_array]
libzrod.GetPredPumpColors.restype = ctypes.c_bool
libzrod.GetPredPumpVelocity.argtypes = [zrodHandle, c_double_array]
libzrod.GetPredPumpVelocity.restype = ctypes.c_bool
libzrod.GetPredPumpVelocityNormalized.argtypes = [zrodHandle, c_double_array]
libzrod.GetPredPumpVelocityNormalized.restype = ctypes.c_bool
libzrod.GetPredPumpChamberPressure.argtypes = [zrodHandle, c_double_array]
libzrod.GetPredPumpChamberPressure.restype = ctypes.c_bool
libzrod.GetPredPumpChamberPressureNormalized.argtypes = [zrodHandle, c_double_array]
libzrod.GetPredPumpChamberPressureNormalized.restype = ctypes.c_bool

libzrod.GetIntermediateCard.argtypes = [zrodHandle, ctypes.c_int, ctypes.c_int, c_double_array, c_double_array]
libzrod.GetIntermediateCard.restype = ctypes.c_bool

libzrod.GetIntermediateTimeSlice.argtypes = [zrodHandle, ctypes.c_int, ctypes.c_int, c_double_array, c_double_array]
libzrod.GetIntermediateTimeSlice.restype = ctypes.c_bool

libzrod.GetPermissibleLoads.argtypes = [zrodHandle, c_double_array, c_double_array, ctypes.c_int, ctypes.c_double, ctypes.c_double]
libzrod.GetPermissibleLoads.restype = ctypes.c_bool

libzrod.GetMeasuredRodLoadingCount.argtypes = [zrodHandle]
libzrod.GetMeasuredRodLoadingCount.restype = ctypes.c_int
libzrod.GetUpscaledRodLoadingCount.argtypes = [zrodHandle]
libzrod.GetUpscaledRodLoadingCount.restype = ctypes.c_int
libzrod.GetPredRodLoadingCount.argtypes = [zrodHandle]
libzrod.GetPredRodLoadingCount.restype = ctypes.c_int

libzrod.GetMeasuredRodLoading.argtypes = [zrodHandle, c_double_array, c_double_array, c_double_array, c_double_array, c_double_array]
libzrod.GetMeasuredRodLoading.restype = ctypes.c_bool
libzrod.GetUpscaledRodLoading.argtypes = [zrodHandle, c_double_array, c_double_array, c_double_array, c_double_array, c_double_array]
libzrod.GetUpscaledRodLoading.restype = ctypes.c_bool
libzrod.GetPredRodLoading.argtypes = [zrodHandle, c_double_array, c_double_array, c_double_array, c_double_array, c_double_array]
libzrod.GetPredRodLoading.restype = ctypes.c_bool

libzrod.GetPuInfo.argtypes = [zrodHandle]
libzrod.GetPuInfo.restype = PuInfo_t
libzrod.SetPuInfo.argtypes = [zrodHandle, PuInfo_t]
libzrod.SetPuInfo.restype = ctypes.c_bool
libzrod.SetPuByName.argtypes = [zrodHandle, ctypes.c_char_p]
libzrod.SetPuByName.restype = ctypes.c_bool

libzrod.SetPuApi.argtypes = [zrodHandle, PuApi_t]
libzrod.SetPuApi.restype = ctypes.c_bool

libzrod.SetFourierCoeffCountPos.argtypes = [zrodHandle, ctypes.c_int]
libzrod.SetFourierCoeffCountLoad.argtypes = [zrodHandle, ctypes.c_int]

libzrod.SetDiagTapers.argtypes = [zrodHandle, ctypes.c_void_p, ctypes.c_int, ctypes.c_double]
libzrod.SetDiagTapers.restype = ctypes.c_bool
libzrod.SetPredTapers.argtypes = [zrodHandle, ctypes.c_void_p, ctypes.c_int, ctypes.c_double]
libzrod.SetPredTapers.restype = ctypes.c_bool

libzrod.SetDiagApiTaperByNumber.argtypes = [zrodHandle, ctypes.c_int, ctypes.c_double, ctypes.c_double]
libzrod.SetDiagApiTaperByNumber.restype = ctypes.c_bool
libzrod.SetPredApiTaperByNumber.argtypes = [zrodHandle, ctypes.c_int, ctypes.c_double, ctypes.c_double]
libzrod.SetPredApiTaperByNumber.restype = ctypes.c_bool

libzrod.SetPredTubings.argtypes = [zrodHandle, ctypes.c_void_p, ctypes.c_int]
libzrod.SetPredTubings.restype = ctypes.c_bool
libzrod.SetDiagTubings.argtypes = [zrodHandle, ctypes.c_void_p, ctypes.c_int]
libzrod.SetDiagTubings.restype = ctypes.c_bool

libzrod.SetCasings.argtypes = [zrodHandle, ctypes.c_void_p, ctypes.c_int]
libzrod.SetCasings.restype = ctypes.c_bool
libzrod.GetCasingCount.argtypes = [zrodHandle]
libzrod.GetCasingCount.restype = ctypes.c_int
libzrod.GetCasings.argtypes = [zrodHandle, ctypes.c_void_p]
libzrod.GetCasings.restype = ctypes.c_bool

libzrod.CalculateFo.argtypes = [zrodHandle]
libzrod.CalculateFo.restype = ctypes.c_double

libzrod.CalculateKrToDepth.argtypes = [zrodHandle, ctypes.c_double]
libzrod.CalculateKrToDepth.restype = ctypes.c_double

'''
libzrod.CalcWaveDiagStepInit.argtypes = [zrodHandle]
libzrod.CalcWaveDiagStepInit.restype = ctypes.c_int #the size of the load & pos arrays to allocate
libzrod.CalcWaveDiagStep.argtypes = [zrodHandle, ctypes.c_int, c_double_array, c_double_array]
libzrod.CalcWaveDiagStep.restype = ctypes.c_bool
libzrod.CalcWaveDiagStepDealloc.argtypes = [zrodHandle]
libzrod.CalcWaveDiagStepDealloc.restype = ctypes.c_bool
'''




@ctypes.CFUNCTYPE(None, ctypes.c_char_p)
def Logfunc(text): print(f"Logfunc: {text.decode('utf-8')}")

class zrod:
    def __new__(cls):
        if(not hasattr(cls, 'instance')):
            cls.instance = super(zrod, cls).__new__(cls)
        else:
            print("WARNING: instance already created. Using the preallocated one.")
        #endif
        return(cls.instance)
    #end __new__()

    def __init__(self):
        self.instance = libzrod.CreateZrodObj()
        libzrod.SetLoggingCallback(Logfunc)
        ver = [ int(num) for num in version("libzrod").split('.')]
        try:
            self.SetClientVersion("py", ver[0], ver[1], ver[2], 0)
        except:
            self.SetClientVersion("pyERR", 0, 0, 0, 0)
            print("Version Error")
        #end try
    #end __init__()

    def __del__(self): libzrod.DeleteZrodObj(self.instance)

    def runzrod(self): libzrod.runzrod(self.instance)
    def Login(self, username, password): return(libzrod.Login(self.instance, str.encode(username), str.encode(password)))
    def Logout(self): return(libzrod.Logout(self.instance))
    def Test(self): libzrod.Test(self.instance)
    def SaveCurrentDesign(self, overwrite): return(libzrod.SaveCurrentDesign(self.instance, overwrite))
    def FetchDesigns(self, fromserver): return(libzrod.FetchDesigns(self.instance, fromserver))
    def GetDesign(self, designId): return(libzrod.GetDesign(self.instance, str.encode(designId)))
    def DeleteDesign(self, designId): return(libzrod.DeleteDesign(self.instance, str.encode(designId)))
    def GetDesigns(self):
        ret = []
        count = self.FetchDesigns(False)  # Get count without fetching from server again
        if count <= 0:
            return(ret)
        #endif
        designs = (DesignInfo_t * count)()
        success = libzrod.GetDesigns(self.instance, designs)
        if success == True:
            for design in designs:
                ret.append(
                    DesignInfo(
                        design.designId.decode(),
                        design.ts.decode(),
                        design.designTitle.decode()
                    )
                )
            #end for
        #endif
        return(ret)
    #end GetDesigns()

    def DeleteZrodObj(self): print("Use pythons del THE_ZROD_INSTANCE")
    def PrintZrodObj(self): libzrod.PrintZrodObj(self.instance)
    def GetZrodVersion(self):
        dest = np.empty(4, dtype=np.int32)
        libzrod.GetZrodVersion(self.instance, dest)
        return(dest)
    #end GetZrodVersion()
    def GetZrodVersionString(self):
        libver = self.GetZrodVersion()
        strlibver = '.'.join(map(str, libver))
        return(strlibver)
    #end GetZrodVersionString
    def DebugZrodObj(self, filepath):
        try:
            if(filepath is None):
                libzrod.DebugZrodObj(self.instance, filepath)
            else:
                libzrod.DebugZrodObj(self.instance, str.encode(filepath))
            #endif
        except:
            print("Debug not available")
        #end try
    #end DebugZrodObj()

    def RunDesign(self): return(libzrod.RunDesign(self.instance))
    def GetWaveResults(self): return(libzrod.GetWaveResults(self.instance))
    def GetWaveParams(self): return(libzrod.GetWaveParams(self.instance))
    def SetWaveParams(self, newParam): return(libzrod.SetWaveParams(self.instance, newParam))
    def GetWaveParamsReadOnly(self): return(libzrod.GetWaveParamsReadOnly(self.instance))
    def GetWaveSettings(self): return(libzrod.GetWaveSettings(self.instance))
    def SetWaveSettings(self, newSettings): return(libzrod.SetWaveSettings(self.instance, newSettings))

    def GetDeviationSurveyCount(self): return(libzrod.GetDeviationSurveyCount(self.instance))
    def GetDeviationSurvey(self):
        surveypoints = self.GetDeviationSurveyCount()
        elems = (DeviationSurveyPoint_t * surveypoints)()
        libzrod.GetDeviationSurvey(self.instance, elems)
        return(elems)
    #end GetDeviationSurvey()

    def SetClientVersion(self, platform, major, minor, revision, build): return(libzrod.SetClientVersion(self.instance, str.encode(platform), major, minor, revision, build))
    def SetDesignTitle(self, newDesignTitle): return(libzrod.SetDesignTitle(self.instance, str.encode(newDesignTitle)))
    def GetDesignTitle(self): return(libzrod.GetDesignTitle(self.instance).decode("ascii"))

    def SetComment(self, newComment): return(libzrod.SetComment(self.instance, str.encode(newComment)))
    def GetComment(self): return(libzrod.GetComment(self.instance).decode("ascii"))

    #def SetDesignID(self, newDesignID): return(libzrod.SetDesignID(self.instance, str.encode(newDesignID)))
    def GetDesignID(self): return(libzrod.GetDesignID(self.instance).decode("ascii"))

    def LoadDyn(self, spm, x_array, y_array):
        if(len(x_array) != len(y_array)): raise ValueError("Array sizes must match")
        if(type(x_array) is not type(y_array)): raise ValueError("Array types must match")
        #make sure theyre doubles
        if(type(x_array) is not "np.float64"): x_array = np.array(x_array, dtype=np.float64)
        if(type(y_array) is not "np.float64"): y_array = np.array(y_array, dtype=np.float64)
        return(libzrod.LoadDyn(self.instance, spm, x_array, y_array, len(x_array)))
    #end LoadDyn()
    def LoadDynFromFileContents(self, dyntext): return(libzrod.LoadDynFromFileContents(self.instance, dyntext))
    def LoadDynFromFile(self, filepath):
        filepath = filepath.replace("~", os.path.expanduser('~'))
        return(libzrod.LoadDynFromFile(self.instance, str.encode(filepath)))
    #end LoadDynFromFile()

    def LoadDynFromDAT(self, filepath):
        filepath = filepath.replace("~", os.path.expanduser('~'))
        print(f"Loading: {filepath}...")
        with open(filepath) as file:
            lines = [line.rstrip() for line in file]
        #end with
        strokelength = lines[5]
        spm = float(lines[8])
        points = int(lines[9])
        print(f"Loaded {points} points.")
        load = []
        pos = []
        for i in range(10, 10+points):
            load.append(float(lines[i]))
            pos.append(float(lines[i+points]))
        #end for
        return(self.LoadDyn(spm, np.array(pos), np.array(load)))
    #end LoadDynFromDAT()

    def WriteDesignFile(self, filepath):
        filepath = filepath.replace("~", os.path.expanduser('~'))
        return(libzrod.WriteDesignFile(self.instance, str.encode(filepath)))
    #end WriteDesignFile()
    def WriteDesignFileWithTemplate(self, filepath, templatepath):
        filepath = filepath.replace("~", os.path.expanduser('~'))
        templatepath = templatepath.replace("~", os.path.expanduser('~'))
        return(libzrod.WriteDesignFileWithTemplate(self.instance, str.encode(filepath), str.encode(templatepath)))
    #end WriteDesignFileWithTemplate()

    def ParseDesignFileContents(self, filecontents, ftype): return(libzrod.ParseDesignFileContents(self.instance, filecontents, ftype))
    def ParseDesignFile(self, filepath):
        filepath = filepath.replace("~", os.path.expanduser('~'))
        return(libzrod.ParseDesignFile(self.instance, str.encode(filepath)))
    #end ParseDesignFile()

    def GetMeasuredDynoPointCount(self): return(libzrod.GetMeasuredDynoPointCount(self.instance))
    def GetMeasuredDyno(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagMeasPointCount
        destX = np.empty(pointcount, dtype=np.float64)
        destY = np.empty(pointcount, dtype=np.float64)
        libzrod.GetMeasuredDyno(self.instance, destX, destY)
        return(destX, destY)
    #end GetMeasuredDyno()
    def GetMeasuredPump(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagMeasPointCount
        destX = np.empty(pointcount, dtype=np.float64)
        destY = np.empty(pointcount, dtype=np.float64)
        libzrod.GetMeasuredPump(self.instance, destX, destY)
        return(destX, destY)
    #end GetMeasuredPump()
    def GetMeasuredPumpColors(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagMeasPointCount
        destC = np.empty(pointcount, dtype=np.int32)
        libzrod.GetMeasuredPumpColors(self.instance, destC)
        return(destC)
    #end GetMeasuredPumpColors()
    def GetMeasuredPumpVelocity(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagMeasPointCount
        destV = np.empty(pointcount, dtype=np.float64)
        libzrod.GetMeasuredPumpVelocity(self.instance, destV)
        return(destV)
    #end GetMeasuredPumpVelocity()
    def GetMeasuredPumpVelocityNormalized(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagMeasPointCount
        destVN = np.empty(pointcount, dtype=np.float64)
        libzrod.GetMeasuredPumpVelocityNormalized(self.instance, destVN)
        return(destVN)
    #end GetMeasuredPumpVelocityNormalized()
    def GetMeasuredPumpChamberPressure(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagMeasPointCount
        destP = np.empty(pointcount, dtype=np.float64)
        libzrod.GetMeasuredPumpChamberPressure(self.instance, destP)
        return(destP)
    #end GetMeasuredPumpChamberPressure()
    def GetMeasuredPumpChamberPressureNormalized(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagMeasPointCount
        destPN = np.empty(pointcount, dtype=np.float64)
        libzrod.GetMeasuredPumpChamberPressureNormalized(self.instance, destPN)
        return(destPN)
    #end GetMeasuredPumpChamberPressureNormalized()

    def SetUpscaledDynoPointCount(self, pointcount): libzrod.SetUpscaledDynoPointCount(self.instance, pointcount)
    def GetUpscaledDynoPointCount(self): return(libzrod.GetUpscaledDynoPointCount(self.instance))
    def GetUpscaledDyno(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagUpscPointCount
        destX = np.empty(pointcount, dtype=np.float64)
        destY = np.empty(pointcount, dtype=np.float64)
        libzrod.GetUpscaledDyno(self.instance, destX, destY)
        return(destX, destY)
    #end GetUpscaledDyno()
    def GetUpscaledPump(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagUpscPointCount
        destX = np.empty(pointcount, dtype=np.float64)
        destY = np.empty(pointcount, dtype=np.float64)
        libzrod.GetUpscaledPump(self.instance, destX, destY)
        return(destX, destY)
    #end GetUpscaledPump()
    def GetUpscaledPumpColors(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagUpscPointCount
        destC = np.empty(pointcount, dtype=np.int32)
        libzrod.GetUpscaledPumpColors(self.instance, destC)
        return(destC)
    #end GetUpscaledPumpColors()
    def GetUpscaledPumpVelocity(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagUpscPointCount
        destV = np.empty(pointcount, dtype=np.float64)
        libzrod.GetUpscaledPumpVelocity(self.instance, destV)
        return(destV)
    #end GetUpscaledPumpVelocity()
    def GetUpscaledPumpVelocityNormalized(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagUpscPointCount
        destVN = np.empty(pointcount, dtype=np.float64)
        libzrod.GetUpscaledPumpVelocityNormalized(self.instance, destVN)
        return(destVN)
    #end GetUpscaledPumpVelocityNormalized()
    def GetUpscaledPumpChamberPressure(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagUpscPointCount
        destP = np.empty(pointcount, dtype=np.float64)
        libzrod.GetUpscaledPumpChamberPressure(self.instance, destP)
        return(destP)
    #end GetUpscaledPumpChamberPressure()
    def GetUpscaledPumpChamberPressureNormalized(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.diagUpscPointCount
        destPN = np.empty(pointcount, dtype=np.float64)
        libzrod.GetUpscaledPumpChamberPressureNormalized(self.instance, destPN)
        return(destPN)
    #end GetUpscaledPumpChamberPressureNormalized()

    def GetPredDynoPointCount(self): return(libzrod.GetPredDynoPointCount(self.instance))
    def GetPredDyno(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.predPointCount
        destX = np.empty(pointcount, dtype=np.float64)
        destY = np.empty(pointcount, dtype=np.float64)
        libzrod.GetPredDyno(self.instance, destX, destY)
        return(destX, destY)
    #end GetPredDyno()
    def GetPredPump(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.predPointCount
        destX = np.empty(pointcount, dtype=np.float64)
        destY = np.empty(pointcount, dtype=np.float64)
        libzrod.GetPredPump(self.instance, destX, destY)
        return(destX, destY)
    #end GetPredPump()
    def GetPredPumpColors(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.predPointCount
        destC = np.empty(pointcount, dtype=np.int32)
        libzrod.GetPredPumpColors(self.instance, destC)
        return(destC)
    #end GetPredPumpColors()
    def GetPredPumpVelocity(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.predPointCount
        destV = np.empty(pointcount, dtype=np.float64)
        libzrod.GetPredPumpVelocity(self.instance, destV)
        return(destV)
    #end GetPredPumpVelocity()
    def GetPredPumpVelocityNormalized(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.predPointCount
        destVN = np.empty(pointcount, dtype=np.float64)
        libzrod.GetPredPumpVelocityNormalized(self.instance, destVN)
        return(destVN)
    #end GetPredPumpVelocityNormalized()
    def GetPredPumpChamberPressure(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.predPointCount
        destP = np.empty(pointcount, dtype=np.float64)
        libzrod.GetPredPumpChamberPressure(self.instance, destP)
        return(destP)
    #end GetPredPumpChamberPressure()
    def GetPredPumpChamberPressureNormalized(self):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = waveParamsRO.predPointCount
        destPN = np.empty(pointcount, dtype=np.float64)
        libzrod.GetPredPumpChamberPressureNormalized(self.instance, destPN)
        return(destPN)
    #end GetPredPumpChamberPressureNormalized()

    def GetIntermediateCard(self, nodeindex, dynotype):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        pointcount = 0
        if(dynotype == 1): #meas
            pointcount = waveParamsRO.diagMeasPointCount
        elif(dynotype == 2): #upsc
            pointcount = waveParamsRO.diagUpscPointCount
        elif(dynotype == 3): #pred
            pointcount = waveParamsRO.predPointCount
        #endif
        destX = np.empty(pointcount, dtype=np.float64)
        destY = np.empty(pointcount, dtype=np.float64)
        libzrod.GetIntermediateCard(self.instance, nodeindex, dynotype, destX, destY)
        return(destX, destY)
    #end GetIntermediateCard()

    def GetIntermediateTimeSlice(self, TimeStep, dynotype):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        nodecount = 0
        if(dynotype == 1): #meas
            nodecount = waveParamsRO.diagMeasM
        elif(dynotype == 2): #upsc
            nodecount = waveParamsRO.diagUpscM
        elif(dynotype == 3): #pred
            nodecount = waveParamsRO.predM
        #endif
        destX = np.empty(nodecount, dtype=np.float64)
        destY = np.empty(nodecount, dtype=np.float64)
        libzrod.GetIntermediateTimeSlice(self.instance, TimeStep, dynotype, destX, destY)
        return(destX, destY)
    #end GetIntermediateTimeSlice()


    def SetDiagApiTaperByNumber(self, apiTaperNumber, pumpDiameter, pumpDepth):
        return(libzrod.SetDiagApiTaperByNumber(self.instance, apiTaperNumber, pumpDiameter, pumpDepth))
    #end SetDiagApiTaperByNumber()
    def SetPredApiTaperByNumber(self, apiTaperNumber, pumpDiameter, pumpDepth):
        return(libzrod.SetPredApiTaperByNumber(self.instance, apiTaperNumber, pumpDiameter, pumpDepth))
    #end SetPredApiTaperByNumber()

    def SetDiagTapers(self, tapers, tapercount, fluidSG):
        return(libzrod.SetDiagTapers(self.instance, tapers, tapercount, fluidSG))
    #end SetDiagTapers()
    def SetPredTapers(self, tapers, tapercount, fluidSG):
        return(libzrod.SetPredTapers(self.instance, tapers, tapercount, fluidSG))
    #end SetPredTapers()
    def xSetDiagTapers(self, tapers, fluidSG):
        return(libzrod.SetDiagTapers(self.instance, ctypes.byref(tapers), len(tapers), fluidSG))
    #end xSetDiagTapers()
    def xSetPredTapers(self, tapers, fluidSG):
        return(libzrod.SetPredTapers(self.instance, ctypes.byref(tapers), len(tapers), fluidSG))
    #end xSetPredTapers()

    def SetDiagTubings(self, tubings, tubingcount):
        return(libzrod.SetDiagTubings(self.instance, tubings, tubingcount))
    #end SetDiagTubings()
    def SetPredTubings(self, tubings, tubingcount):
        return(libzrod.SetPredTubings(self.instance, tubings, tubingcount))
    #end SetPredTubings()
    def xSetDiagTubings(self, tubings):
        return(libzrod.SetDiagTubings(self.instance, ctypes.byref(tubings), len(tubings)))
    #end xSetDiagTubings()
    def xSetPredTubings(self, tubings):
        return(libzrod.SetPredTubings(self.instance, ctypes.byref(tubings), len(tubings)))
    #end xSetPredTubings()

    def SetCasings(self, casings, casingcount):
        return(libzrod.SetCasings(self.instance, casings, casingcount))
    #end SetCasings()
    def xSetCasings(self, casings):
        return(libzrod.SetCasings(self.instance, ctypes.byref(casings), len(casings)))
    #end xSetCasings()
    def GetCasingCount(self):
        return(libzrod.GetCasingCount(self.instance))
    #end GetCasingCount()
    def GetCasings(self):
        count = self.GetCasingCount()
        if count <= 0:
            return []
        casings = (CasingBase_t * count)()
        libzrod.GetCasings(self.instance, casings)
        return casings
    #end GetCasings()

    def GetPermissibleLoads(self, destX, destY, pointcount, clipmin, clipmax):
        return(libzrod.GetPermissibleLoads(self.instance, destX, destY, pointcount, clipmin, clipmax))
    #end GetPermissibleLoads()

    def GetMeasuredRodLoadingCount(self): return(libzrod.GetMeasuredRodLoadingCount(self.instance))
    def GetUpscaledRodLoadingCount(self): return(libzrod.GetUpscaledRodLoadingCount(self.instance))
    def GetPredRodLoadingCount(self): return(libzrod.GetPredRodLoadingCount(self.instance))

    def xGetMeasuredRodLoading(self):
        pointcount = libzrod.GetMeasuredRodLoadingCount(self.instance)
        destDepth = np.empty(pointcount, dtype=np.float64)
        destLbsMax = np.empty(pointcount, dtype=np.float64)
        destLbsMin = np.empty(pointcount, dtype=np.float64)
        destPctMax = np.empty(pointcount, dtype=np.float64)
        destPctMin = np.empty(pointcount, dtype=np.float64)
        libzrod.GetMeasuredRodLoading(self.instance, destDepth, destLbsMax, destLbsMin, destPctMax, destPctMin)
        return(destDepth, destLbsMax, destLbsMin, destPctMax, destPctMin)
    #end xGetMeasuredRodLoading()
    def xGetUpscaledRodLoading(self):
        pointcount = libzrod.GetUpscaledRodLoadingCount(self.instance)
        destDepth = np.empty(pointcount, dtype=np.float64)
        destLbsMax = np.empty(pointcount, dtype=np.float64)
        destLbsMin = np.empty(pointcount, dtype=np.float64)
        destPctMax = np.empty(pointcount, dtype=np.float64)
        destPctMin = np.empty(pointcount, dtype=np.float64)
        libzrod.GetUpscaledRodLoading(self.instance, destDepth, destLbsMax, destLbsMin, destPctMax, destPctMin)
        return(destDepth, destLbsMax, destLbsMin, destPctMax, destPctMin)
    #end xGetUpscaledRodLoading()
    def xGetPredRodLoading(self):
        pointcount = libzrod.GetPredRodLoadingCount(self.instance)
        destDepth = np.empty(pointcount, dtype=np.float64)
        destLbsMax = np.empty(pointcount, dtype=np.float64)
        destLbsMin = np.empty(pointcount, dtype=np.float64)
        destPctMax = np.empty(pointcount, dtype=np.float64)
        destPctMin = np.empty(pointcount, dtype=np.float64)
        libzrod.GetPredRodLoading(self.instance, destDepth, destLbsMax, destLbsMin, destPctMax, destPctMin)
        return(destDepth, destLbsMax, destLbsMin, destPctMax, destPctMin)
    #end xGetPredRodLoading()

    def GetPuInfo(self): return(libzrod.GetPuInfo(self.instance))
    def SetPuInfo(self, newPuInfo): return(libzrod.SetPuInfo(self.instance, newPuInfo))
    def SetPuByName(self, newpuname): return(libzrod.SetPuByName(self.instance, newpuname))
    def SetPuApi(self, newPuApi): return(libzrod.SetPuApi(self.instance, newPuApi))

    def SetFourierCoeffCountPos(self,  count): libzrod.SetFourierCoeffCountPos(self.instance, count)
    def SetFourierCoeffCountLoad(self, count): libzrod.SetFourierCoeffCountLoad(self.instance, count)

    def CalculateFo(self): return(libzrod.CalculateFo(self.instance))
    def CalculateKrToDepth(self, depth): return(libzrod.CalculateKrToDepth(self.instance, depth))


    def CalculateTotalRodLength(taper_array):
        if not taper_array or len(taper_array) < 2: return 0.0

        total_length = 0.0
        for index in range(len(taper_array) - 1):
            # Support both dict access and attribute access
            if isinstance(taper_array[index], dict):
                start_depth_current = taper_array[index]['startDepth']
                start_depth_next = taper_array[index + 1]['startDepth']
            else:
                start_depth_current = taper_array[index].startDepth
                start_depth_next = taper_array[index + 1].startDepth
            #endif
            segment_length = start_depth_next - start_depth_current
            total_length += segment_length
        return total_length
    #end CalculateTotalRodLength()

    '''
    #TODO: delete these... theyre obsolete
    #for incrimental calcs. used for animations and really big datasets (or for live/realtime calcs).
    def CalcWaveDiagStepInit(self): return(libzrod.CalcWaveDiagStepInit(self.instance))
    def CalcWaveDiagStep(self, TimeStep):
        waveParamsRO = libzrod.GetWaveParamsReadOnly(self.instance)
        nodecount = waveParamsRO.diagMeasM
        load = np.empty(nodecount, dtype=np.float64)
        pos = np.empty(nodecount, dtype=np.float64)
        result = libzrod.CalcWaveDiagStep(self.instance, TimeStep, load, pos)
        return(result, load, pos)
    #end CalcWaveDiagStep()
    def CalcWaveDiagStepDealloc(self): return(libzrod.CalcWaveDiagStepDealloc(self.instance))
    '''
#end zrod
