import mongoose from 'mongoose';import {app} from './app.js';import {config} from './config.js';
try{await mongoose.connect(config.mongoUri);app.listen(config.port,()=>console.log('ShiftSync API listening on '+config.port))}catch(error){console.error('Database connection failed:',error.message);process.exit(1)}
