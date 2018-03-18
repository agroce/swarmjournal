set terminal postscript enhanced color solid lw 2 "Times-Roman" 20
set output "graph.ps"
set key left
set xlabel "hours"
set ylabel "distinct crashes"
plot [0:168] [0:] "noswarm.txt", "swarm.txt", "swarm_avg.txt" w lines, "noswarm_avg.txt" w lines
