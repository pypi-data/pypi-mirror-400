import ctypes
import os
import sys

import numpy
import ailia
import ailia.audio

import urllib.request
import ssl
import shutil
import os
import platform

#### dependency check
if sys.platform == "win32":
    import ctypes
    try:
        for library in ["vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll"]:
            ctypes.windll.LoadLibrary(library)
    except:
        print("  WARNING Please install MSVC 2015-2019 runtime from https://docs.microsoft.com/ja-jp/cpp/windows/latest-supported-vc-redist")


#### loading DLL / DYLIB / SO  ####
if sys.platform == "win32":
    dll_platform = "windows/x64"
    dll_name = "ailia_voice.dll"
    load_fn = ctypes.WinDLL
elif sys.platform == "darwin":
    dll_platform = "mac"
    dll_name = "libailia_voice.dylib"
    load_fn = ctypes.CDLL
else:
    is_arm = "arm" in platform.machine() or platform.machine() == "aarch64"
    if is_arm:
        if platform.architecture()[0] == "32bit":
            dll_platform = "linux/armeabi-v7a"
        else:
            dll_platform = "linux/arm64-v8a"
    else:
        dll_platform = "linux/x64"
    dll_name = "libailia_voice.so"
    load_fn = ctypes.CDLL

dll_found = False
candidate = ["", str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep), str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep) + dll_platform + str(os.sep)]
for dir in candidate:
    try:
        dll = load_fn(dir + dll_name)
        dll_found = True
    except:
        pass
if not dll_found:
    msg = "DLL load failed : \'" + dll_name + "\' is not found"
    raise ImportError(msg)

# ==============================================================================

from ctypes import *

AILIA_VOICE_STATUS_SUCCESS = ( 0 )

AILIA_VOICE_DICTIONARY_TYPE_OPEN_JTALK = (0)
AILIA_VOICE_DICTIONARY_TYPE_G2P_EN = (1)

AILIA_VOICE_MODEL_TYPE_TACOTRON2 = (0)
AILIA_VOICE_MODEL_TYPE_GPT_SOVITS = (1)

AILIA_VOICE_CLEANER_TYPE_BASIC = (0)
AILIA_VOICE_CLEANER_TYPE_ENGLISH = (1)

AILIA_VOICE_G2P_TYPE_GPT_SOVITS_EN = (1)
AILIA_VOICE_G2P_TYPE_GPT_SOVITS_JA = (2)

AILIA_VOICE_FLAG_NONE = (0)

AILIA_VOICE_API_CALLBACK_VERSION = (2)

AILIA_VOICE_USER_API_AILIA_AUDIO_RESAMPLE = CFUNCTYPE((c_int), POINTER(c_float), POINTER(c_float), c_int, c_int, c_int, c_int)
AILIA_VOICE_USER_API_AILIA_AUDIO_GET_RESAMPLE_LEN = CFUNCTYPE((c_int), POINTER(c_int), c_int, c_int, c_int)
AILIA_VOICE_USER_API_AILIA_CREATE = CFUNCTYPE((c_int), POINTER(c_void_p), c_int, c_int)
AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_FILE_A = CFUNCTYPE((c_int), c_void_p, c_char_p)
AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_FILE_W = CFUNCTYPE((c_int), c_void_p, POINTER(c_wchar))
AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_MEM = CFUNCTYPE((c_int), c_void_p, POINTER(c_byte), c_uint)
AILIA_VOICE_USER_API_AILIA_SET_MEMORY_MODE = CFUNCTYPE((c_int), c_void_p, c_uint)
AILIA_VOICE_USER_API_AILIA_DESTROY = CFUNCTYPE((None), c_void_p)
AILIA_VOICE_USER_API_AILIA_UPDATE = CFUNCTYPE((c_int), c_void_p)
AILIA_VOICE_USER_API_AILIA_GET_BLOB_INDEX_BY_INPUT_INDEX = CFUNCTYPE((c_int), c_void_p, POINTER(c_uint), c_uint)
AILIA_VOICE_USER_API_AILIA_GET_BLOB_INDEX_BY_OUTPUT_INDEX = CFUNCTYPE((c_int), c_void_p, POINTER(c_uint), c_uint)
AILIA_VOICE_USER_API_AILIA_GET_BLOB_DATA = CFUNCTYPE((c_int), c_void_p, POINTER(c_float), c_uint, c_uint)
AILIA_VOICE_USER_API_AILIA_SET_INPUT_BLOB_DATA = CFUNCTYPE((c_int), c_void_p, POINTER(c_float), c_uint, c_uint)
AILIA_VOICE_USER_API_AILIA_SET_INPUT_BLOB_SHAPE = CFUNCTYPE((c_int), c_void_p, c_void_p, c_uint, c_uint)
AILIA_VOICE_USER_API_AILIA_GET_INPUT_BLOB_COUNT = CFUNCTYPE((c_int), c_void_p, POINTER(c_uint))
AILIA_VOICE_USER_API_AILIA_GET_OUTPUT_BLOB_COUNT = CFUNCTYPE((c_int), c_void_p, POINTER(c_uint))
AILIA_VOICE_USER_API_AILIA_GET_BLOB_SHAPE = CFUNCTYPE((c_int), c_void_p, c_void_p, c_uint, c_uint)
AILIA_VOICE_USER_API_AILIA_GET_ERROR_DETAIL = CFUNCTYPE((c_char_p), c_void_p)
AILIA_VOICE_USER_API_AILIA_COPY_BLOB_DATA = CFUNCTYPE((c_int), c_void_p, c_uint, c_void_p, c_uint)

class struct__AILIAVoiceApiCallback(Structure):
    pass

struct__AILIAVoiceApiCallback.__slots__ = [
    'ailiaAudioResample',
    'ailiaAudioGetResampleLen',
    'ailiaCreate',
    'ailiaOpenWeightFileA',
    'ailiaOpenWeightFileW',
    'ailiaOpenWeightMem',
    'ailiaSetMemoryMode',
    'ailiaDestroy',
    'ailiaUpdate',
    'ailiaGetBlobIndexByInputIndex',
    'ailiaGetBlobIndexByOutputIndex',
    'ailiaGetBlobData',
    'ailiaSetInputBlobData',
    'ailiaSetInputBlobShape',
    'ailiaGetBlobShape',
    'ailiaGetInputBlobCount',
    'ailiaGetOutputBlobCount',
    'ailiaGetErrorDetail',
    'ailiaCopyBlobData',
]
struct__AILIAVoiceApiCallback._fields_ = [
    ('ailiaAudioResample', AILIA_VOICE_USER_API_AILIA_AUDIO_RESAMPLE),
    ('ailiaAudioGetResampleLen', AILIA_VOICE_USER_API_AILIA_AUDIO_GET_RESAMPLE_LEN),
    ('ailiaCreate', AILIA_VOICE_USER_API_AILIA_CREATE),
    ('ailiaOpenWeightFileA', AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_FILE_A),
    ('ailiaOpenWeightFileW', AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_FILE_W),
    ('ailiaOpenWeightMem', AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_MEM),
    ('ailiaSetMemoryMode', AILIA_VOICE_USER_API_AILIA_SET_MEMORY_MODE),
    ('ailiaDestroy', AILIA_VOICE_USER_API_AILIA_DESTROY),
    ('ailiaUpdate', AILIA_VOICE_USER_API_AILIA_UPDATE),
    ('ailiaGetBlobIndexByInputIndex', AILIA_VOICE_USER_API_AILIA_GET_BLOB_INDEX_BY_INPUT_INDEX),
    ('ailiaGetBlobIndexByOutputIndex', AILIA_VOICE_USER_API_AILIA_GET_BLOB_INDEX_BY_OUTPUT_INDEX),
    ('ailiaGetBlobData', AILIA_VOICE_USER_API_AILIA_GET_BLOB_DATA),
    ('ailiaSetInputBlobData', AILIA_VOICE_USER_API_AILIA_SET_INPUT_BLOB_DATA),
    ('ailiaSetInputBlobShape', AILIA_VOICE_USER_API_AILIA_SET_INPUT_BLOB_SHAPE),
    ('ailiaGetBlobShape', AILIA_VOICE_USER_API_AILIA_GET_BLOB_SHAPE),
    ('ailiaGetInputBlobCount', AILIA_VOICE_USER_API_AILIA_GET_INPUT_BLOB_COUNT),
    ('ailiaGetOutputBlobCount', AILIA_VOICE_USER_API_AILIA_GET_OUTPUT_BLOB_COUNT),
    ('ailiaGetErrorDetail', AILIA_VOICE_USER_API_AILIA_GET_ERROR_DETAIL),
    ('ailiaCopyBlobData', AILIA_VOICE_USER_API_AILIA_COPY_BLOB_DATA),
]

AILIAVoiceApiCallback = struct__AILIAVoiceApiCallback

# ==============================================================================

dll.ailiaVoiceCreate.restype = c_int
dll.ailiaVoiceCreate.argtypes = (POINTER(c_void_p), c_int32, c_int32, c_int32, c_int32, AILIAVoiceApiCallback, c_int32)

dll.ailiaVoiceDestroy.restype = None
dll.ailiaVoiceDestroy.argtypes = (c_void_p, )

dll.ailiaVoiceSetUserDictionaryFileA.restype = c_int
dll.ailiaVoiceSetUserDictionaryFileA.argtypes = (c_void_p, c_char_p, c_int32)

dll.ailiaVoiceSetUserDictionaryFileW.restype = c_int
dll.ailiaVoiceSetUserDictionaryFileW.argtypes = (c_void_p, c_wchar_p, c_int32)

dll.ailiaVoiceOpenDictionaryFileA.restype = c_int
dll.ailiaVoiceOpenDictionaryFileA.argtypes = (c_void_p, c_char_p, c_int32)

dll.ailiaVoiceOpenDictionaryFileW.restype = c_int
dll.ailiaVoiceOpenDictionaryFileW.argtypes = (c_void_p, c_wchar_p, c_int32)

dll.ailiaVoiceOpenModelFileA.restype = c_int
dll.ailiaVoiceOpenModelFileA.argtypes = (c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int32, c_int32)

dll.ailiaVoiceOpenModelFileW.restype = c_int
dll.ailiaVoiceOpenModelFileW.argtypes = (c_void_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_int32, c_int32)

dll.ailiaVoiceGraphemeToPhoneme.restype = c_int
dll.ailiaVoiceGraphemeToPhoneme.argtypes = (c_void_p, c_char_p, c_int32)

dll.ailiaVoiceGetFeatureLength.restype = c_int
dll.ailiaVoiceGetFeatureLength.argtypes = (c_void_p, POINTER(c_uint32))

dll.ailiaVoiceGetFeatures.restype = c_int
dll.ailiaVoiceGetFeatures.argtypes = (c_void_p, numpy.ctypeslib.ndpointer(
                dtype=numpy.byte, flags='CONTIGUOUS'
            ),                               # text
            ctypes.c_uint)

dll.ailiaVoiceSetReference.restype = c_int
dll.ailiaVoiceSetReference.argtypes = (c_void_p, numpy.ctypeslib.ndpointer(
                dtype=numpy.float32, flags='CONTIGUOUS'
            ),                               # wave
            ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, c_char_p)

dll.ailiaVoiceInference.restype = c_int
dll.ailiaVoiceInference.argtypes = (c_void_p, c_char_p)

dll.ailiaVoiceGetWaveInfo.restype = c_int
dll.ailiaVoiceGetWaveInfo.argtypes = (c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32))

dll.ailiaVoiceGetWave.restype = c_int
dll.ailiaVoiceGetWave.argtypes = (c_void_p, numpy.ctypeslib.ndpointer(
                dtype=numpy.float32, flags='CONTIGUOUS'
            ),                               # wave
            ctypes.c_uint)

# ==============================================================================
# model download
# ==============================================================================

def progress_print(block_count, block_size, total_size):
    percentage = 100.0 * block_count * block_size / total_size
    if percentage > 100:
        # Bigger than 100 does not look good, so...
        percentage = 100
    max_bar = 50
    bar_num = int(percentage / (100 / max_bar))
    progress_element = '=' * bar_num
    if bar_num != max_bar:
        progress_element += '>'
    bar_fill = ' '  # fill the blanks
    bar = progress_element.ljust(max_bar, bar_fill)
    total_size_kb = total_size / 1024
    print(f'[{bar} {percentage:.2f}% ( {total_size_kb:.0f}KB )]', end='\r')

def urlretrieve(remote_path, weight_path, progress_print):
    temp_path = weight_path + ".tmp"
    try:
        #raise ssl.SSLError # test
        urllib.request.urlretrieve(
            remote_path,
            temp_path,
            progress_print,
        )
    except ssl.SSLError as e:
        print(f'SSLError detected, so try to download without ssl')
        remote_path = remote_path.replace("https","http")
        urllib.request.urlretrieve(
            remote_path,
            temp_path,
            progress_print,
        )
    shutil.move(temp_path, weight_path)

def check_and_download_file(file_path, remote_path):
    if not os.path.exists(file_path):
        print('Downloading %s...' % file_path)
        urlretrieve(remote_path + os.path.basename(file_path), file_path, progress_print)

# ==============================================================================
# base model class
# ==============================================================================

class AiliaVoiceError(RuntimeError):
    def __init__(self, message, code):
        super().__init__(f"{message} code:{code}")
        self.code = code

class AiliaVoiceModel:
    _api_callback = None
    _instance = None

    def _check(self, status):
        if status != AILIA_VOICE_STATUS_SUCCESS:
            raise AiliaVoiceError(f"ailia voice error", status)

    def _string_buffer_aw(self, path):
        if sys.platform == "win32":
            return ctypes.create_unicode_buffer(path)
        else:
            return ctypes.create_string_buffer(path.encode("utf-8"))

    def _string_buffer(self, path):
        return ctypes.create_string_buffer(path.encode("utf-8"))

    def _create_callback(self):
        callback = AILIAVoiceApiCallback()
        callback.ailiaAudioResample = AILIA_VOICE_USER_API_AILIA_AUDIO_RESAMPLE(("ailiaAudioResample", ailia.audio.audio_core.dll))
        callback.ailiaAudioGetResampleLen = AILIA_VOICE_USER_API_AILIA_AUDIO_GET_RESAMPLE_LEN(("ailiaAudioGetResampleLen", ailia.audio.audio_core.dll))
        callback.ailiaCreate = AILIA_VOICE_USER_API_AILIA_CREATE(("ailiaCreate", ailia.core.dll))
        callback.ailiaOpenWeightFileA = AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_FILE_A(("ailiaOpenWeightFileA", ailia.core.dll))
        callback.ailiaOpenWeightFileW = AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_FILE_W(("ailiaOpenWeightFileW", ailia.core.dll))
        callback.ailiaOpenWeightMem = AILIA_VOICE_USER_API_AILIA_OPEN_WEIGHT_MEM(("ailiaOpenWeightMem", ailia.core.dll))
        callback.ailiaSetMemoryMode = AILIA_VOICE_USER_API_AILIA_SET_MEMORY_MODE(("ailiaSetMemoryMode", ailia.core.dll))
        callback.ailiaDestroy = AILIA_VOICE_USER_API_AILIA_DESTROY(("ailiaDestroy", ailia.core.dll))
        callback.ailiaUpdate = AILIA_VOICE_USER_API_AILIA_UPDATE(("ailiaUpdate", ailia.core.dll))
        callback.ailiaGetBlobIndexByInputIndex = AILIA_VOICE_USER_API_AILIA_GET_BLOB_INDEX_BY_INPUT_INDEX(("ailiaGetBlobIndexByInputIndex", ailia.core.dll))
        callback.ailiaGetBlobIndexByOutputIndex = AILIA_VOICE_USER_API_AILIA_GET_BLOB_INDEX_BY_OUTPUT_INDEX(("ailiaGetBlobIndexByOutputIndex", ailia.core.dll))
        callback.ailiaGetBlobData = AILIA_VOICE_USER_API_AILIA_GET_BLOB_DATA(("ailiaGetBlobData", ailia.core.dll))
        callback.ailiaSetInputBlobData = AILIA_VOICE_USER_API_AILIA_SET_INPUT_BLOB_DATA(("ailiaSetInputBlobData", ailia.core.dll))
        callback.ailiaSetInputBlobShape = AILIA_VOICE_USER_API_AILIA_SET_INPUT_BLOB_SHAPE(("ailiaSetInputBlobShape", ailia.core.dll))
        callback.ailiaGetBlobShape = AILIA_VOICE_USER_API_AILIA_GET_BLOB_SHAPE(("ailiaGetBlobShape", ailia.core.dll))
        callback.ailiaGetInputBlobCount = AILIA_VOICE_USER_API_AILIA_GET_INPUT_BLOB_COUNT(("ailiaGetInputBlobCount", ailia.core.dll))
        callback.ailiaGetOutputBlobCount = AILIA_VOICE_USER_API_AILIA_GET_OUTPUT_BLOB_COUNT(("ailiaGetOutputBlobCount", ailia.core.dll))
        callback.ailiaGetErrorDetail = AILIA_VOICE_USER_API_AILIA_GET_ERROR_DETAIL(("ailiaGetErrorDetail", ailia.core.dll))
        callback.ailiaCopyBlobData = AILIA_VOICE_USER_API_AILIA_COPY_BLOB_DATA(("ailiaCopyBlobData", ailia.core.dll))
        self._api_callback = callback # prevent GC

# ==============================================================================
# Public class
# ==============================================================================

class G2P(AiliaVoiceModel):
    """Constructor of ailia Voice model instance.

    Parameters
    ----------
    env_id : int, optional, default: ENVIRONMENT_AUTO(-1)
        environment id of ailia execution.
        To retrieve env_id value, use
            ailia.get_environment_count() / ailia.get_environment() pair
        or
            ailia.get_gpu_environment_id() .
    num_thread : int, optional, default: MULTITHREAD_AUTO(0)
        number of threads.
        valid values:
            MULTITHREAD_AUTO=0 [means systems's logical processor count],
            1 to 32.
    memory_mode : int, optional, default: 11 (reuse interstage)
        memory management mode of ailia execution.
        To retrieve memory_mode value, use ailia.get_memory_mode() .
    flags : int, optional, default: AILIA_VOICE_FLAG_NONE
        Reserved
    """
    def __init__(self, env_id = -1, num_thread = 0, memory_mode = 11, flags = AILIA_VOICE_FLAG_NONE):
        self._instance = ctypes.c_void_p(None)
        self._create_callback()
        self._check(dll.ailiaVoiceCreate(cast(pointer(self._instance), POINTER(c_void_p)), ctypes.c_int32(env_id), ctypes.c_int32(num_thread), ctypes.c_int32(memory_mode), ctypes.c_int32(flags), self._api_callback, ctypes.c_int32(AILIA_VOICE_API_CALLBACK_VERSION)))

    def initialize_model(self, model_path = "./", user_dict_path = None):
        """ Initialize and download the model.

        Parameters
        ----------
        model_path : string, optional, default: "./"
            Destination for saving the model file
        user_dict_path : string, optional, default: None
            Specify the path of the user dictionary. The user dictionary is in mecab format.
        """
        if "time_license" in ailia.get_version():
            ailia.check_and_download_license()
        if user_dict_path is not None:
            self._set_user_dictionary(user_dict_path)
        self._download_dictionary(model_path)
        self._open_dictionary(model_path + "open_jtalk_dic_utf_8-1.11", model_path + "g2p_en")
    
    def _download_dictionary(self, model_path):
        REMOTE_PATH = "https://storage.googleapis.com/ailia-models/open_jtalk/open_jtalk_dic_utf_8-1.11/"
        os.makedirs(model_path + "open_jtalk_dic_utf_8-1.11", exist_ok = True)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/COPYING", REMOTE_PATH)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/char.bin", REMOTE_PATH)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/left-id.def", REMOTE_PATH)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/matrix.bin", REMOTE_PATH)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/pos-id.def", REMOTE_PATH)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/rewrite.def", REMOTE_PATH)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/right-id.def", REMOTE_PATH)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/sys.dic", REMOTE_PATH)
        check_and_download_file(model_path + "open_jtalk_dic_utf_8-1.11/unk.dic", REMOTE_PATH)

        REMOTE_PATH = "https://storage.googleapis.com/ailia-models/g2p_en/"
        os.makedirs(model_path + "g2p_en", exist_ok = True)
        check_and_download_file(model_path + "g2p_en/averaged_perceptron_tagger_classes.txt", REMOTE_PATH)
        check_and_download_file(model_path + "g2p_en/averaged_perceptron_tagger_tagdict.txt", REMOTE_PATH)
        check_and_download_file(model_path + "g2p_en/averaged_perceptron_tagger_weights.txt", REMOTE_PATH)
        check_and_download_file(model_path + "g2p_en/cmudict", REMOTE_PATH)
        check_and_download_file(model_path + "g2p_en/homographs.en", REMOTE_PATH)
        check_and_download_file(model_path + "g2p_en/g2p_decoder.onnx", REMOTE_PATH)
        check_and_download_file(model_path + "g2p_en/g2p_encoder.onnx", REMOTE_PATH)

    def _set_user_dictionary(self, path_ja):
        if sys.platform == "win32":
            self._check(dll.ailiaVoiceSetUserDictionaryFileW(self._instance, self._string_buffer_aw(path_ja), AILIA_VOICE_DICTIONARY_TYPE_OPEN_JTALK))
        else:
            self._check(dll.ailiaVoiceSetUserDictionaryFileA(self._instance, self._string_buffer_aw(path_ja), AILIA_VOICE_DICTIONARY_TYPE_OPEN_JTALK))

    def _open_dictionary(self, path_ja, path_en):
        if sys.platform == "win32":
            self._check(dll.ailiaVoiceOpenDictionaryFileW(self._instance, self._string_buffer_aw(path_ja), AILIA_VOICE_DICTIONARY_TYPE_OPEN_JTALK))
            self._check(dll.ailiaVoiceOpenDictionaryFileW(self._instance, self._string_buffer_aw(path_en), AILIA_VOICE_DICTIONARY_TYPE_G2P_EN))
        else:
            self._check(dll.ailiaVoiceOpenDictionaryFileA(self._instance, self._string_buffer_aw(path_ja), AILIA_VOICE_DICTIONARY_TYPE_OPEN_JTALK))
            self._check(dll.ailiaVoiceOpenDictionaryFileA(self._instance, self._string_buffer_aw(path_en), AILIA_VOICE_DICTIONARY_TYPE_G2P_EN))

    def g2p(self, text, g2p_type):
        """ Generates phonemes from text.

        Parameters
        ----------
        text : string
            Input text
        g2p_type : int
            Format of G2P. Specify with AILIA_VOICE_G2P_TYPE_GPT_SOVITS_*.
        """
        self._check(dll.ailiaVoiceGraphemeToPhoneme(self._instance, self._string_buffer(text), g2p_type))

        count = ctypes.c_uint(0)
        self._check(dll.ailiaVoiceGetFeatureLength(self._instance, ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int8, order='C')

        self._check(dll.ailiaVoiceGetFeatures(self._instance, buf, count))

        text = bytes(buf[0:len(buf) - 1]).decode("utf-8")
        return text

    def __del__(self):
        if self._instance:
            dll.ailiaVoiceDestroy(cast(self._instance, c_void_p))

class GPTSoVITS(G2P):
    def initialize_model(self, model_path = "./", user_dict_path = None):
        """ Initialize and download the model.

        Parameters
        ----------
        model_path : string, optional, default: "./"
            Destination for saving the model file.
        user_dict_path : string, optional, default: None
            Specify the path of the user dictionary. The user dictionary is in mecab format.
        """
        if "time_license" in ailia.get_version():
            ailia.check_and_download_license()
        self._download_dictionary(model_path)
        self._download_model(model_path)
        if user_dict_path is not None:
            self._set_user_dictionary(user_dict_path)
        self._open_dictionary(model_path + "open_jtalk_dic_utf_8-1.11", model_path + "g2p_en")
        self._open_model(model_path + "t2s_encoder.onnx", model_path + "t2s_fsdec.onnx", model_path + "t2s_sdec.opt3.onnx", model_path + "vits.onnx", model_path + "cnhubert.onnx")
    
    def _download_model(self, model_path):
        REMOTE_PATH = "https://storage.googleapis.com/ailia-models/gpt-sovits/"
        os.makedirs(model_path, exist_ok = True)
        check_and_download_file(model_path + "t2s_encoder.onnx", REMOTE_PATH)
        check_and_download_file(model_path + "t2s_fsdec.onnx", REMOTE_PATH)
        check_and_download_file(model_path + "t2s_sdec.opt3.onnx", REMOTE_PATH)
        check_and_download_file(model_path + "vits.onnx", REMOTE_PATH)
        check_and_download_file(model_path + "cnhubert.onnx", REMOTE_PATH)

    def _open_model(self, encoder, decoder1, decoder2, wave, ssl):
        p1 = self._string_buffer_aw(encoder)
        p2 = self._string_buffer_aw(decoder1)
        p3 = self._string_buffer_aw(decoder2)
        p4 = self._string_buffer_aw(wave)
        p5 = self._string_buffer_aw(ssl)

        if sys.platform == "win32":
            self._check(dll.ailiaVoiceOpenModelFileW(self._instance, p1, p2, p3, p4, p5, AILIA_VOICE_MODEL_TYPE_GPT_SOVITS, AILIA_VOICE_CLEANER_TYPE_BASIC))
        else:
            self._check(dll.ailiaVoiceOpenModelFileA(self._instance, p1, p2, p3, p4, p5, AILIA_VOICE_MODEL_TYPE_GPT_SOVITS, AILIA_VOICE_CLEANER_TYPE_BASIC))

    def set_reference_audio(self, ref_text, g2p_type, audio_waveform, sampling_rate):
        """ Specify the voice that will serve as the timbre for speech synthesis.

        Parameters
        ----------
        ref_text : string,
            Text of the speech content in the audio PCM.
        g2p_type : int
            Format of G2P. Specify with AILIA_VOICE_G2P_TYPE_GPT_SOVITS_*.
        audio_waveform : np.ndarray
            PCM data, formatted as either `(num_samples)` or `(channels, num_samples)`.
        sampling_rate : int
            Sampling rate (Hz).
        """

        if g2p_type is not None:
            ref_text = self.g2p(ref_text, g2p_type)
        p6 = self._string_buffer(ref_text)

        if len(audio_waveform.shape) == 1:
            channels = 1
        elif len(audio_waveform.shape) == 2:
            channels = audio_waveform.shape[0]
            audio_waveform = numpy.transpose(audio_waveform, (1, 0)).flatten()
        else:
            raise AiliaVoiceError(f"audio_waveform must be 1 channel or 2 channel", -1)

        audio_waveform = numpy.ascontiguousarray(audio_waveform.astype(numpy.float32))

        self._check(dll.ailiaVoiceSetReference(self._instance, audio_waveform, audio_waveform.nbytes, channels, sampling_rate, p6))
        
    def synthesize_voice(self, text, g2p_type):
        """ Synthesizes voice from input text.

        Parameters
        ----------
        text : string
            Input text.
        g2p_type : int
            Format of G2P. Specify with AILIA_VOICE_G2P_TYPE_GPT_SOVITS_*.

        Returns
        ----------
        buf : np.ndarray
            PCM data, formatted as either `(num_samples)`.
        sampling_rate : int
            Sampling rate (Hz).
        """

        if g2p_type is not None:
            text = self.g2p(text, g2p_type)
        
        if text == "":
            return None, 0

        p6 = self._string_buffer(text)

        self._check(dll.ailiaVoiceInference(self._instance, p6))

        samples = ctypes.c_uint(0)
        channels = ctypes.c_uint(0)
        sampling_rate = ctypes.c_uint(0)
        self._check(dll.ailiaVoiceGetWaveInfo(self._instance, ctypes.byref(samples), ctypes.byref(channels),ctypes.byref(sampling_rate)))

        buf = numpy.zeros((samples.value * channels.value), dtype=numpy.float32, order='C')

        self._check(dll.ailiaVoiceGetWave(self._instance, buf, buf.nbytes))

        return buf, sampling_rate.value

