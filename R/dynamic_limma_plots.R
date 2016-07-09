# Author: John B Damask
# Created: May 2016
# Purpose: Generic script to create n-number of volcano plots per limma contrasts

library(tidyr)
library(ggplot2)
library(gridExtra)
xtest <- read.table(args[1], header=TRUE, fill=TRUE, sep="\t")
colnames(xtest) <- gsub("\\.{3}", " - ", colnames(xtest))
xtest.tidier <- xtest %>% gather(key, VALUE, -Genes, -A, -F, -F.p.value)
## Funky regexp with lookahead to make sure we split on last "."
xtest.tidy <- xtest.tidier %>% separate(key, into=c("MEASUREMENT", "CONTRAST"), sep = "\\.(?=[^.]*$)")
x.tidy <- xtest.tidy %>% spread(MEASUREMENT, VALUE, fill="", convert = TRUE)
head(x.tidy)
x.tidy$threshold <- as.factor(abs(x.tidy$Coef) > 1 & x.tidy$p.value.adj < 0.1) 
c <- unique(x.tidy$CONTRAST)
p <- lapply(c, FUN=function(x){
  ggplot(data=x.tidy[which(x.tidy$CONTRAST == x),], aes(x=Coef, y=-log10(p.value.adj), 
         colour=threshold))  +    geom_point(alpha=0.4, size=1.75) +
    labs(title = x) + xlab("log2 fold change") + ylab("-log10 adjusted p-value") 
})
grid.arrange(grobs=p)
