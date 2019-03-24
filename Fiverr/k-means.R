#########################################################
# import libraries
#########################################################

library(data.table)
library(ggplot2)
library(plotly)

#########################################################
# load data
#########################################################

yeast <- fread("yeast.txt",header = F, stringsAsFactors = F)
colnames(yeast) <- c("Sequence Name","mcg","gvh","alm","mit","erl","pox","vac","nuc","Class Distribution") 
yeast %>%
  ggplot(aes(x=alm,y=mit,color=`Class Distribution`)) + 
  geom_point()
# kmeans code
yeast_cluster <- kmeans(yeast[,2:9], # we are only considering column#2 to 9 as the remaining columns have the id and class name which can't be used for clustering
                        2)# we are keepiing the value of clusters as 2 as for 2 we are getting a good seperation
# plotting te clusters
plot_ly(x=yeast$mcg,y=yeast$gvh,z=yeast$alm,type = "scatter3d",mode="markers",color = yeast_cluster$cluster)

#########################################################
# rough work
#########################################################

# trying different values of k
for(i in 1:10){
  print(paste("Number of clusters = ",i))
  yeast_cluster <- kmeans(yeast[,2:9], i)
  print(yeast_cluster$tot.withinss)
  yeast %>%
    ggplot(aes(x=alm,y=mit,color=yeast_cluster$cluster)) +
    geom_point()
}
