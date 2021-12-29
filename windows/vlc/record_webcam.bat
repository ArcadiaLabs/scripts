:: Starts recording the webcam immediately, or stops recording if already running
:: Please set "only one instance" in VLC settings for the script to work

echo off

:: vlc.exe location
SET vlc="C:\Program Files\VideoLAN\VLC\vlc.exe"

:: creates filename with current date(y-m-d_H-M-S)
SET datetime=%date:~-4%-%date:~3,2%-%date:~0,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
:: creates current time(d-m-Y_H:M:S) for stream
SET sfilter="marq{marquee='%%d-%%m-%%Y_%%H:%%M:%%S',position=6,size=20}"

:: Settings
SET file1=D:\\%datetime%_capture.mp4
SET cam1="WEBCAM SKILLKORP SKP_W-10"
SET mic1="Microphone (Microphone SKILLKORP SKP_W-10)"
SET caching1="0"
SET args1="--qt-start-minimized"

:: Clean exit of VLC if already running
tasklist /fi "imagename eq vlc.exe" |find ":" > nul
if errorlevel 1 start "cam1" %vlc% vlc://quit&exit

start "cam1" %vlc% dshow:// :dshow-vdev=%cam1% :dshow-adev=%mic1% :dshow-aspect-ratio="16\:9" --sout "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100,sfilter=%sfilter%}:file{dst=%file1%,no-overwrite}" --sout-mux-caching=%caching1% %args1%