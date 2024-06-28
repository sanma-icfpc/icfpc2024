IF "%VCINSTALLDIR%" == "" CALL "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" || EXIT /B 1
@echo off
setlocal

echo Building fmt
pushd %~dp0
pushd %~dp0\fmt
if not exist vsbuild mkdir vsbuild
pushd vsbuild
cmake .. -G "Visual Studio 17 2022" -DFMT_UNICODE=ON || exit /b 1
cmake --build . --config Debug -- /p:CharacterSet=Unicode || exit /b 1
cmake --build . --config Release -- /p:CharacterSet=Unicode || exit /b 1
popd
popd

echo Building gflags
pushd %~dp0
if not exist gflags_vsbuild mkdir gflags_vsbuild
cmake -S gflags -B gflags_vsbuild -DBUILD_SHARED_LIBS=OFF -DBUILD_STATIC_LIBS=ON -DBUILD_TESTING=OFF --install-prefix=%cd%\gflags_vsbuild -G "Visual Studio 17 2022" || exit /b 1
cmake --build gflags_vsbuild --config Debug || exit /b 1
cmake --build gflags_vsbuild --config Release || exit /b 1
popd

echo Building glog
pushd %~dp0
if not exist glog_vsbuild mkdir glog_vsbuild
cmake -S glog -B glog_vsbuild -DWITH_GFLAGS=ON -DBUILD_SHARED_LIBS=OFF -DBUILD_TESTING=OFF -DHAVE_LIB_GFLAGS=1 --install-prefix=%cd%\glog_vsbuild -G "Visual Studio 17 2022" || exit /b 1
cmake --build glog_vsbuild --config Debug || exit /b 1
cmake --build glog_vsbuild --config Release || exit /b 1
popd

echo Building gtest
pushd %~dp0
if not exist gtest_vsbuild mkdir gtest_vsbuild
cmake -S gtest -B gtest_vsbuild -DBUILD_GMOCK=OFF -G "Visual Studio 17 2022" || exit /b 1
cmake --build gtest_vsbuild --config Debug || exit /b 1
cmake --build gtest_vsbuild --config Release || exit /b 1
popd

endlocal