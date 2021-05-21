cd C:\gstreamer\1.0\x86_64\bin 
.\gst-launch-1.0 -v udpsrc port=3001 caps="application/x-rtp, encoding-name=(string)JPEG,payload=96" ! rtpjpegdepay ! jpegdec ! autovideosink