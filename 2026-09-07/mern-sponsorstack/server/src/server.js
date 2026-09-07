import mongoose from'mongoose';import{app}from'./app.js';import{config}from'./config.js';await mongoose.connect(config.mongoUri);app.listen(config.port,()=>console.log('SponsorStack API listening on '+config.port));

