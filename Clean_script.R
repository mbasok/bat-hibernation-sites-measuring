library(dplyr)
library(ggplot2)
library(lme4)
library(mgcv)
#library(ggeffects) <- some settings were changed while I was working on the text, didn't work again
library(lmerTest)
library(sjPlot)
library(car)

library(lubridate)
library(MASS)
library(segmented)

library(marginaleffects)

## Load dataset
Probability_df <- read.csv("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Probability_dataframe.csv", header = T, sep = ",")


#### Correlation matrix ####

Correlation_df <- Probability_df[,c('Area', "Perimeter", 'Entrance_distance', "Volume",
                                    'Entrances_number')]
Correlation_df <- unique(Correlation_df)
cor(Correlation_df)

#                       Area Perimeter Entrance_distance    Volume Entrances_number
#Area              1.0000000 0.9337223         0.6872456 0.9773980        0.5979178
#Perimeter         0.9337223 1.0000000         0.6726707 0.8658356        0.6687682
#Entrance_distance 0.6872456 0.6726707         1.0000000 0.6413440        0.2919602
#Volume            0.9773980 0.8658356         0.6413440 1.0000000        0.5651339
#Entrances_number  0.5979178 0.6687682         0.2919602 0.5651339        1.0000000





#### PROBABILITY MODELS ####

pr_m_1 <- glmer(Probability ~ New_species*(Area)
                + (1|ID), data = Probability_df,
                family = binomial)

pr_m_2 <- glmer(Probability ~ New_species*(Perimeter)
                + (1|ID), data = Probability_df,
                family = binomial)

pr_m_3 <- glmer(Probability ~ New_species*(Entrance_distance)
                + (1|ID), data = Probability_df,
                family = binomial)

pr_m_4 <- glmer(Probability ~ New_species*(Volume)
                + (1|ID), data = Probability_df,
                family = binomial)

pr_m_5 <- glmer(Probability ~ New_species*(Entrances_number)
                + (1|ID), data = Probability_df,
                family = binomial)

#### Comparing AICs probability models ####
AIC(pr_m_1, pr_m_2, pr_m_3, pr_m_4, pr_m_5)


#       df      AIC
#pr_m_1  7 1355.996  Area
#pr_m_2  7 1347.927  Perimeter
#pr_m_3  7 1322.145  Length           <- this model is the best
#pr_m_4  7 1363.640  Volume
#pr_m_5  7 1354.877  Entrances number


#### Summary model length on probability ####
summary(pr_m_3)

#Random effects:
#  Groups Name        Variance Std.Dev.
#ID     (Intercept) 2.28     1.51    
#Number of obs: 2124, groups:  ID, 69


#Fixed effects:
#                                     Estimate Std. Error z value Pr(>|z|)    
# (Intercept)                         -0.61676    0.68593  -0.899  0.36856    
# New_speciesMyotis                   -8.80348    0.81298 -10.829  < 2e-16 ***
# New_speciesPaur                     -6.31386    0.74902  -8.429  < 2e-16 ***
# Entrance_distance                    0.15764    0.05544   2.844  0.00446 ** 
# New_speciesMyotis:Entrance_distance  0.32659    0.05472   5.969 2.39e-09 ***
# New_speciesPaur:Entrance_distance    0.11811    0.05220   2.263  0.02364 *  
#  ---
#  Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1






#### ABUNDANCE MODELS ####

#Loading dataframe

Abundance_df <- read.csv("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Abundance_dataframe.csv", header = T, sep = ",")


# Fitting the models
ab_m_1 <- glmer.nb(Bat_number ~ New_species*Area + (1|ID),
               data = Abundance_df)

ab_m_2 <- glmer.nb(Bat_number ~ New_species*Perimeter + (1|ID),
                   data = Abundance_df)

ab_m_3 <- glmer.nb(Bat_number ~ New_species*Entrance_distance + (1|ID),
                   data = Abundance_df)

ab_m_4 <- glmer.nb(Bat_number ~ New_species*Volume + (1|ID),
                   data = Abundance_df)

ab_m_5 <- glmer.nb(Bat_number ~ New_species*Entrances_number + (1|ID),
                   data = Abundance_df)


#### Comparing AICs abundance models ####
AIC(ab_m_1, ab_m_2, ab_m_3, ab_m_4, ab_m_5)

#       df      AIC
#ab_m_1  8 4205.297  Area
#ab_m_2  8 4140.246  Perimeter
#ab_m_3  8 3882.165  Length           <- this one is the best
#ab_m_4  8 8895.880  Volume
#ab_m_5  8 4123.288  Entrances number


#### Summary model abundance and length ####
summary(ab_m_3)

#Random effects:
#  Groups Name        Variance Std.Dev.
#ID     (Intercept) 0.7415   0.8611  
#Number of obs: 2124, groups:  ID, 69

#Fixed effects:
#                                     Estimate Std. Error z value Pr(>|z|)    
# (Intercept)                         -0.31138    0.34327  -0.907   0.3643    
# New_speciesMyotis                   -7.51715    0.33772 -22.259  < 2e-16 ***
# New_speciesPaur                     -5.16089    0.38070 -13.556  < 2e-16 ***
# Entrance_distance                    0.04771    0.02639   1.808   0.0706 .  
# New_speciesMyotis:Entrance_distance  0.39768    0.01812  21.952  < 2e-16 ***
# New_speciesPaur:Entrance_distance    0.15948    0.02110   7.557 4.12e-14 ***
#  ---
#  Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1




#### TEMPERATURE MODELS ####
#For these models, I took mean temperature in the furthermost part of th bunkers
#recorded during January-February only.

#Loading data
Temperature_df <- read.csv("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Temperature_dataframe.csv", header = T, sep = ",")


#### Mean temperature and length ####

mt_di_m_3 <- glmer.nb(Bat_number ~ New_species*Entrance_distance + New_species*mean_temp + 
                        (1|ID),
                      data = subset(Temperature_df, New_species != "Paur"))

summary(mt_di_m_3)

#Random effects:
#Groups Name        Variance Std.Dev.
#ID     (Intercept) 0.02943  0.1716  
#Number of obs: 28, groups:  ID, 14
#
#Fixed effects:
#                                    Estimate Std. Error z value Pr(>|z|)    
#(Intercept)                          0.56533    0.49934   1.132    0.258    
#New_speciesMyotis                   -7.17196    1.29125  -5.554 2.79e-08 ***
#Entrance_distance                    0.01890    0.02697   0.701    0.483    
#mean_temp                            0.03011    0.08142   0.370    0.712    
#New_speciesMyotis:Entrance_distance  0.02795    0.05075   0.551    0.582    
#New_speciesMyotis:mean_temp          1.84238    0.36977   4.983 6.27e-07 ***
#  ---
#  Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1





#### Temperature range ####
t_range_m1 <- glmer.nb(Bat_number ~ New_species*temp_range + 
                          (1|ID),
                        data = subset(Temperature_df, New_species != "Paur"))


summary(t_range_m1)








#### SPACE USAGE MODEL ####
#Loading dataframe

Spatial_df <- read.csv("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Spatial_dataframe.csv", header = T, sep = ",")

#Fitting the model
sp_m_1 <- glmer(Relative_distance ~ New_species*Area + (1|ID),
                data = subset(Spatial_df, New_species == 'Enil'|
                                New_species == 'Myotis'), family = binomial)

sp_m_2 <- glmer(Relative_distance ~ New_species*Perimeter + (1|ID),
                data = subset(Spatial_df, New_species == 'Enil'|
                                New_species == 'Myotis'), family = binomial)

sp_m_3 <- glmer(Relative_distance ~ New_species*Entrance_distance + (1|ID),
                    data = subset(Spatial_df, New_species == 'Enil'|
                                    New_species == 'Myotis'), family = binomial)

sp_m_4 <- glmer(Relative_distance ~ New_species*Volume + (1|ID),
                data = subset(Spatial_df, New_species == 'Enil'|
                                New_species == 'Myotis'), family = binomial)

sp_m_5 <- glmer(Relative_distance ~ New_species*Entrances_number + (1|ID),
                data = subset(Spatial_df, New_species == 'Enil'|
                                New_species == 'Myotis'), family = binomial)

#### Comparing AICs spatial models ####
AIC(sp_m_1, sp_m_2, sp_m_3, sp_m_4, sp_m_5)

#       df      AIC
#sp_m_1  5 3750.942 Area
#sp_m_2  5 3753.361 Perimeter
#sp_m_3  5 3745.412 Length        <- this model is the best
#sp_m_4  5 3749.105 Volume
#sp_m_5  5 3750.947 Entrances number







#### VISUALIZATION ####



#### 1. Probability model ####


#Calculate predicted probability based on the model
predict_prob <- plot_predictions(
  pr_m_3,
  condition = c("Entrance_distance", "New_species"),
  draw = FALSE
)

head(predict_prob)



#The plot itself
Prob_plot <- ggplot(data = predict_prob, aes(x = Entrance_distance, y = estimate))+
  geom_point(data = na.omit(Probability_df), 
             aes(x = Entrance_distance, y=Probability, colour = New_species), alpha=0.2, size = 0.7)+
  geom_line(aes(colour= New_species), size = 0.5)+
  geom_ribbon(aes(ymin = conf.low, ymax = conf.high, fill = New_species), alpha=0.3)+
  coord_cartesian(ylim = c(0,1))+
  labs(x = "Bunker length (m)",
       y = "Predicted probability",
       colour = "",
       fill = "")+
  theme_minimal()+
  theme(
    axis.ticks = element_line(color = "black"),
    axis.line = element_line(color = "black", linewidth = 0.3), # 2. Force axis lines back
    axis.title.x = element_text(colour = "black"),
    axis.title.y = element_text(colour = "black"),
    axis.text.x = element_text(colour = "black"),
    axis.text.y = element_text(colour = "black"),
    legend.text = element_text(colour = "black", face = 'italic')
  ) +
  scale_color_manual(
    values = c("Enil" = 'goldenrod',
               "Myotis" = 'purple3',
               "Paur" = 'pink2'),
    labels = c("Enil" = "E. nilssonii",
               "Myotis" = "Myotis sp.",
               "Paur" = "P. auritus"))+
  scale_fill_manual(
    values = c("Enil" = 'goldenrod',
               "Myotis" = 'purple3',
               "Paur" = 'pink2'),
    labels = c("Enil" = "E. nilssonii",
               "Myotis" = "Myotis sp.",
               "Paur" = "P. auritus"))+
  theme(legend.position = "bottom", 
        legend.title = element_blank())


ggsave("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Fig.1. Probability_plot.jpg", plot = Prob_plot, width = 83, height = 100, units="mm", dpi = 1000)


#### 2. Abundance ####



#Calculate predicted abundance based on the model
predict_abund <- plot_predictions(
  ab_m_3,
  condition = c("Entrance_distance", "New_species"),
  draw = FALSE
)


#Plot for all species 
Abund_plot <- ggplot(data = predict_abund, 
       aes(x = Entrance_distance, y = estimate, colour = New_species, fill = New_species))+
  facet_wrap(~New_species, nrow = 1, scales = "free_y")+
  geom_point(data = na.omit(Abundance_df), 
             aes(x = Entrance_distance, y = Bat_number), 
             alpha=0.2, size = 0.7)+
  geom_line(size = 0.5)+
  geom_ribbon(aes(ymin = conf.low, ymax = conf.high), colour = NA, alpha=0.3)+
  labs(x = "Bunker length (m)",
       y = "Predicted number of bats")+
  #coord_cartesian(ylim = c(0, 80))+
  theme_minimal()+
  theme(
    axis.ticks = element_line(color = "black"),
    axis.line = element_line(color = "black", linewidth = 0.3), 
    axis.title.x = element_text(colour = "black"),
    axis.title.y = element_text(colour = "black"),
    axis.text.x = element_text(colour = "black"),
    axis.text.y = element_text(colour = "black"),
    legend.title = element_text(colour = "black"),
    legend.text = element_text(colour = "black", face = 'italic')
  )+
  scale_color_manual(
    values = c("Enil" = 'goldenrod',
               "Myotis" = 'purple3',
               "Paur" = 'pink2'),
    labels = c("Enil" = "E. nilssonii",
               "Myotis" = "Myotis sp.",
               "Paur" = "P. auritus"))+
  scale_fill_manual(
    values = c("Enil" = 'goldenrod',
               "Myotis" = 'purple3',
               "Paur" = 'pink2'),
    labels = c("Enil" = "E. nilssonii",
               "Myotis" = "Myotis sp.",
               "Paur" = "P. auritus"))+
  theme(legend.position = "bottom", 
        legend.title = element_blank(),
        strip.background = element_blank(),  strip.text.x = element_blank())


ggsave("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Fig.2.Abundance_plot.jpg", plot = Abund_plot, width = 180, height = 100, units="mm", dpi = 1000)







#### 3. Temperature ####

#### 3.1 Mean temperature ####
predict_mtemp <- plot_predictions(
  mt_di_m_3,
  condition = c("mean_temp", "New_species"),
  draw = FALSE
)


#### 3.1.1 Plot for Myotis bats ####
Plot_meant <- ggplot(data = subset(predict_mtemp, New_species == "Myotis"),
                     aes(x = mean_temp, y = estimate))+
  geom_point(data = na.omit(subset(Temperature_df, New_species=="Myotis")),
             aes(x=mean_temp, y = Bat_number), colour = 'purple', alpha = 0.2, size = 0.7)+
  geom_line(size = 0.5, colour = 'purple')+
  geom_ribbon(aes(ymin = conf.low, ymax = conf.high), fill = 'purple', alpha=0.3)+
  theme_minimal()+
  labs(x = "Mean T (°C)",
       y = "Predicted number of bats",
       tag = "A")+
  theme(
    axis.ticks = element_line(color = "black"),
    axis.line = element_line(color = "black", linewidth = 0.3),
    axis.title.x = element_text(colour = "black"),
    axis.title.y = element_text(colour = "black"),
    axis.text.x = element_text(colour = "black"),
    axis.text.y = element_text(colour = "black"),
    plot.tag = element_text(face = "bold")
  )+
  theme(legend.position = "bottom")




#### 3.2 Temperature range ####
pred_t_range <- plot_predictions(
  t_range_m1,
  condition = c("temp_range", "New_species"),
  draw = FALSE
)




#### 3.2.1. Plot for Myotis ####

Plot_ranget <- ggplot(data = subset(pred_t_range, New_species=='Myotis'), 
                       aes(x = temp_range, y = estimate))+
  geom_point(data = na.omit(subset(Temperature_df, New_species=="Myotis")),
             aes(x=temp_range, y = Bat_number), colour = 'purple', alpha = 0.2, size = 0.7)+
  geom_line(size = 0.5, colour = 'purple')+
  geom_ribbon(aes(ymin = conf.low, ymax = conf.high), fill = 'purple', alpha=0.3)+
  theme_minimal()+
  labs(x = "T range (°C)",
       y = "Predicted number of bats",
       tag = "B")+
  theme(
    plot.tag = element_text(face = "bold"),
    axis.ticks = element_line(color = "black"),
    axis.line = element_line(color = "black", linewidth = 0.3),
    axis.title.x = element_text(colour = "black"),
    axis.title.y = element_blank(),
    axis.text.x = element_text(colour = "black"),
    axis.text.y = element_blank(),
    legend.position = "bottom")+
  scale_x_continuous(breaks = seq(0, max(Temperature_df$temp_range), by = 3))


#Combining two plots
temperature_plot <- Plot_meant + Plot_ranget

#Saving the plot
ggsave("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Fig.3.Temperature_plot.jpg", plot = temperature_plot, width = 80, height = 65, units="mm", dpi = 1000)





#### 4. Space usage ####
#### 4.1 Preparations ####
predict_space <- plot_predictions(
  sp_m_3,
  condition = c("Entrance_distance", "New_species"),
  draw = FALSE
)


#Indicating min and max distance at which species were found
mEnil <- min(subset(na.omit(Spatial_df), New_species=="Enil")$Entrance_distance)
MEnil <- max(subset(na.omit(Spatial_df), New_species=="Enil")$Entrance_distance)
mMyotis <- min(subset(na.omit(Spatial_df), New_species=="Myotis")$Entrance_distance)
MMyotis <- max(subset(na.omit(Spatial_df), New_species=="Myotis")$Entrance_distance)

#Downloading dataframe with real number of bats in clusters to show the distribution of
#groups in relation to the bunker length

Groups_df <- read.csv("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Groups_dataframe.csv", header = T, sep = ",")

Groups_df$New_species <- case_when(
  Groups_df$Species == 'Mdau' | Groups_df$Species == 'Mmbra'|
    Groups_df$Species == 'Myotis sp' ~ 'Myotis', 
  TRUE ~ Groups_df$Species)


#Removing unidentified bats
Groups_df <- Groups_df %>%
  filter(New_species != 'Chi sp' & New_species != 'Chiroptera sp')
  
  
#Checking if the species left are correct
as.factor(Groups_df$New_species)
levels(Groups_df$New_species)


#Saving the dataframe
write.csv(Groups_df, "C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Groups_dataframe.csv", row.names = F)



#### 4.2 The plot itself ####
library(grid)

Space_plot <- ggplot(data = subset(predict_space, New_species == 'Enil' & Entrance_distance >= mEnil & Entrance_distance <= MEnil |
                       New_species == 'Myotis' & Entrance_distance >= mMyotis & Entrance_distance <= MMyotis), 
       aes(x = Entrance_distance, y = estimate))+
  geom_point(data = subset(na.omit(Groups_df), New_species=="Enil" | 
                             New_species=="Myotis"), 
             aes(x = Entrance_distance, y=Distance/Entrance_distance, 
                 fill = New_species, size = Number_of_bats), 
             shape = 21, colour = "black", alpha=0.2)+
  scale_size(range = c(0.5,4), name = "Group size:")+
  geom_line(aes(colour= New_species), size = 0.5)+
  geom_ribbon(aes(ymin = conf.low, ymax = conf.high, fill = New_species), alpha=0.3)+
  scale_y_continuous(limits = c(0, 1))+
  labs(x = "Bunker length (m)",
       y = "Relative distance from entrance",
       colour = NULL,
       fill = NULL)+
  theme_minimal()+
  theme(
    axis.ticks = element_line(color = "black"),
    axis.line = element_line(color = "black", linewidth = 0.3),
    axis.title.x = element_text(colour = "black"),
    axis.title.y = element_text(colour = "black"),
    axis.text.x = element_text(colour = "black"),
    axis.text.y = element_text(colour = "black"),
    legend.title = element_text(colour = "black"),
    legend.text = element_text(colour = "black", face = 'italic')
  )+
  scale_color_manual(
    values = c("Enil" = 'goldenrod',
               "Myotis" = 'purple3'),
    labels = c("Enil" = "E. nilssonii",
               "Myotis" = "Myotis sp."))+
  scale_fill_manual(
    values = c("Enil" = 'goldenrod',
               "Myotis" = 'purple3'),
    labels = c("Enil" = "E. nilssonii",
               "Myotis" = "Myotis sp."))+
  theme(legend.position = "bottom",
        legend.box = "vertical",
        legend.key.size = unit(0.4, "cm"),
        legend.spacing.x = unit(0.02, "cm"),
        legend.spacing.y = unit(0.02, "cm"))+
  guides(fill = guide_legend(order = 1),
         colour = guide_legend(order = 1),
         size = guide_legend(order = 2))
  
#Look at the plot
Space_plot

#Saving the plot
ggsave("C:/Users/m7627/Desktop/9.04.2022/Рукокрылые/PhD/Chapter 1/For excel and R/0. Clean files and script/Fig.4.Space_plot.jpg", plot = Space_plot, width = 80, height = 100, units="mm", dpi = 1000)

