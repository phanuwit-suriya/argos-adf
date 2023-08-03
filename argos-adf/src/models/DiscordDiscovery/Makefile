#Requires numpy-source: numpy.i, arrayobjects.h, _arrayobjects.h

#Uncomment below line if you want to build the CUDA version as well
#GPU = 1

TARGET   = _naive_dd.so
SWIG_SRC = naive_dd.i
######################### SOURCE INFORMATION #################################
# naive_dd.cpp        Original serial implementation with only single-frame detection
# naive_dd_mt.cpp     Original Multi-thread implementation with only single-frame detection
# naive_dd_common.cpp Common methods for 'naive_dd_cpu.cpp' and 'naive_dd_gpu.cu' 
# naive_dd_cpu.cpp    Multi-thread implementation with single-/multi-frame detection
# naive_dd_gpu.cu     GPU implementation using CUDA with single-/multi-frame detection
# ############################################################################
CPP_SRC  = naive_dd.cpp\
           naive_dd_mt.cpp\
           naive_dd_common.cpp\
           naive_dd_cpu.cpp
CUDA_SRC = naive_dd_gpu.cu

############################# UBUNTU #########################################
PYTHON_INCLUDE     = -I/usr/include/python3.5
NUMPY_CORE_INCLUDE = -I../../../../numpy/numpy/core/include/ -I/usr/local/lib/python3.5/dist-packages/numpy/core/include
############################# CENTOS #########################################
#PYTHON_INCLUDE     = -I/usr/include/python3.6m
#NUMPY_CORE_INCLUDE = -I../../../../numpy/numpy/core/include/ -I/usr/lib64/python3.5/site-packages/numpy/core/include
##############################################################################

SWIG_INTRM = $(SWIG_SRC:.i=.py)  $(SWIG_SRC:.i=_wrap.c)
CPP_INTRM  = $(SWIG_SRC:.i=_wrap.o) $(CPP_SRC:.cpp=.o)
NVCC_INTRM = $(CUDA_SRC:.cu=.o)

ifeq ($(GPU), 1)
	ALL_INTRM    = $(CPP_INTRM) $(SWIG_INTRM) $(NVCC_INTRM)
	BUILD_INTRM  = $(CPP_INTRM) $(NVCC_INTRM)
	SWIG = swig
	CPP  = g++
	NVCC = nvcc
	LD   = nvcc
	RM   = rm
	NVCC_LD_PFLAGS = --cudart=static -Wno-deprecated-gpu-targets
	SWIG_GPU_FLAG = -D_GPU
else
	ALL_INTRM   = $(CPP_INTRM) $(SWIG_INTERM)
	BUILD_INTRM = $(CPP_INTRM)
	SWIG = swig
	CPP  = g++
	LD   = g++
	RM   = rm
	SWIG_GPU_FLAG =
endif

SWIG_PFLAGS = -python $(SWIG_GPU_FLAG)
SWIG_SFLAGS = 
CPP_PFLAGS  = -c -fPIC -O2
CPP_SFLAGS  = $(PYTHON_INCLUDE) $(NUMPY_CORE_INCLUDE)
LD_PFLAGS   = --shared $(NVCC_LD_PFLAGS)
LD_SFLAGS   = -lpthread
RM_PFLAGS   = -f
NVCC_PFLAGS = -c -O2 --compiler-options "$(CPP_PFLAGS)" -Wno-deprecated-gpu-targets

all: $(ALL_INTRM)
	$(LD) $(LD_PFLAGS) $(BUILD_INTRM) -o $(TARGET) $(LD_SFLAGS)

clean:
	$(RM) $(RM_PFLAGS) $(TARGET) $(SWIG_INTRM) $(CPP_INTRM) $(NVCC_INTRM)

%.py %_wrap.c:%.i
	$(SWIG) $(SWIG_PFLAGS) $< $(SWIG_SFLAGS)

%.o:%.cpp
	$(CPP) $(CPP_PFLAGS) $< $(CPP_SFLAGS)
	
%.o:%.c
	$(CPP) $(CPP_PFLAGS) $< $(CPP_SFLAGS)

%.o:%.cu
	$(NVCC) $(NVCC_PFLAGS) $< $(CPP_SFLAGS)
	
