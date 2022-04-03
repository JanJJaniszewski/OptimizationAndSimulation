library(pacman)
p_load(ggplot2, arrow, tidyverse)

# LOADING DATA
df1 <- arrow::read_feather('/Users/pole1/PycharmProjects/Optimization/data/results_testrun.feather')
df2 <- arrow::read_feather('/Users/pole1/PycharmProjects/Optimization/data/waitingtimes_testrun.feather')

# TOTAL

# Queues 
df1 %>% group_by(clock) %>% summarise(queue = sum(queue)) %>% ggplot(aes(x=clock, y=queue)) + geom_line() + geom_smooth()

# Waiting time
df2 %>% ggplot(aes(x=clock, y=waiting_time)) + geom_line() + geom_smooth()

# Mean queue
df1 %>% summarise(queue = mean(queue))

# Mean waiting time
df2 %>% summarise(waiting_time = mean(waiting_time))



# BY ROAD
# Queues
for (r in df1$road %>% unique()){
  print(df2 %>% filter(road == r) %>% ggplot(aes(x=clock, y=waiting_time)) + geom_line())
}

# Waiting time
for (r in df1$road %>% unique()){
  print(df1 %>% filter(road == r) %>% ggplot(aes(x=clock, y=queue)) + geom_line())
}

# Mean queue
df1 %>% group_by(road) %>% summarise(queue = mean(queue))

# Mean waiting time
df2 %>% group_by(road) %>% summarise(waiting_time = mean(waiting_time))
