import sys
import os
import matplotlib.pyplot as plt


data = []

scales = []
basic_mem_list = []
basic_cpu_list = []

effi_mem_list = []
effi_cpu_list = []


input_dir, basic_outdir, effi_outdir = sys.argv[1:]



for root, dirs, files in os.walk(input_dir):
    for file in files:            
            inf = os.path.join(root, file)
            outf = file.replace("in", "output")
            basic_outf = os.path.join(basic_outdir, outf)
            effi_outf = os.path.join(effi_outdir, outf)

            with open(inf) as f:
                lines = f.readlines()
                s1 = len(lines[0])-1
                s2 = 0
                j = 0
                k = 0
                for i, line in enumerate(lines[1:]):
                    
                    if line[0].isalpha():
                        j = i
                        k = len(lines[i+2:])
                        s2 = len(lines[i+1])-1
                        break

            l = [s1*(2**j)+ s2*(2**k) ]
            # print(inf, lines, s1, j, s2, k, l)
            with open(basic_outf) as bf:
                cpu_time, mem = bf.readlines()[3:5]
                l.append(float(mem))
                l.append(float(cpu_time))

            with open(effi_outf) as ef:
                cpu_time, mem = ef.readlines()[3:5]
                l.append(float(mem))
                l.append(float(cpu_time))
                
            data.append(l)


data.sort()
# print(data)
for item in data:
    a,b,c,d,e = item[:]
    scales.append(a)
    basic_mem_list.append(b)
    basic_cpu_list.append(c)
    effi_mem_list.append(d)
    effi_cpu_list.append(e)


plt.figure()
plt.plot(scales, basic_mem_list, label='basic algo')
plt.scatter(scales, basic_mem_list)
plt.plot(scales, effi_mem_list, label='efficient algo')
plt.scatter(scales, effi_mem_list)
plt.xlabel('size: M+N')
plt.ylabel('memory (KB)')
plt.title('Graph1 – Memory vs Problem Size (M+N)')
plt.legend()
plt.savefig('memory.png')



#
plt.figure()
plt.plot(scales, basic_cpu_list, label='basic algo')
plt.scatter(scales, basic_cpu_list)
plt.plot(scales, effi_cpu_list, label='efficient algo')
plt.scatter(scales, effi_cpu_list)
plt.ylabel('time (ms)')
plt.xlabel('size: M+N')
plt.title('Graph2 – Time vs Problem Size (M+N)')
plt.legend()
plt.savefig('time.png')

# print(scales)