library(pacman)
p_load(ggplot2, arrow, tidyverse)

df1 <- arrow::read_feather('/Users/pole1/PycharmProjects/Optimization/data/results_testrun.feather')

df1 %>% filter(road == 'we') %>% ggplot(aes(x=clock, y=queue)) + geom_line()
df1 %>% filter(road == 'ew') %>% ggplot(aes(x=clock, y=queue)) + geom_line()

df1 %>% group_by(clock) %>% summarise(queue = sum(queue)) %>% ggplot(aes(x=clock, y=queue)) + geom_line()

df2 <- arrow::read_feather('/Users/pole1/PycharmProjects/Optimization/data/waitingtimes_testrun.feather')

df2 %>% group_by(road) %>% summarise(waiting_time = mean(waiting_time))
