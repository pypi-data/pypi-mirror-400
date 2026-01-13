# sudo perf stat -d -d -d record ./App -b -i ../models/MNIST.ai-dan
sudo perf stat -d -d -d record ./App -t -o tmp

# sudo perf record -e iTLB-load-misses ./App
