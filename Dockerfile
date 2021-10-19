# https://hub.docker.com/r/cwaffles/openpose
FROM nvidia/cuda:10.0-cudnn7-devel

#get deps
RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
python3-dev python3-pip git g++ wget make libprotobuf-dev protobuf-compiler libopencv-dev \
libgoogle-glog-dev libboost-all-dev libcaffe-cuda-dev libhdf5-dev libatlas-base-dev

#for python api
#RUN pip3 install numpy opencv-python 

#replace cmake as old version has CUDA variable bugs
RUN wget https://github.com/Kitware/CMake/releases/download/v3.16.0/cmake-3.16.0-Linux-x86_64.tar.gz && \
tar xzf cmake-3.16.0-Linux-x86_64.tar.gz -C /opt && \
rm cmake-3.16.0-Linux-x86_64.tar.gz
ENV PATH="/opt/cmake-3.16.0-Linux-x86_64/bin:${PATH}"

#get openpose
WORKDIR /openpose
ADD . .
# RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git .

#build it ,without Python API
WORKDIR /openpose/build
RUN cmake
	    -DDOWNLOAD_BODY_25_MODEL=ON \
        -DDOWNLOAD_BODY_MPI_MODEL=OFF \
        -DDOWNLOAD_HAND_MODEL=OFF \
        -DDOWNLOAD_FACE_MODEL=OFF \
	    .. 

RUN sed -ie 's/set(AMPERE "80 86")/#&/g'  ../cmake/Cuda.cmake && \
    sed -ie 's/set(AMPERE "80 86")/#&/g'  ../3rdparty/caffe/cmake/Cuda.cmake
#Compilation
RUN make -j `nproc`
WORKDIR /openpose

RUN pip3 install -r requirements.txt
CMD python3 openposeSvr.py & ./build/examples/openpose/openpose.bin --video examples/media/video.avi --write_json "people_Data" --display 0 --render_pose 0
