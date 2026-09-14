import mongoose from 'mongoose';
const opts={timestamps:true};
export const Tenant=mongoose.model('Tenant',new mongoose.Schema({name:{type:String,required:true,trim:true}},opts));
export const User=mongoose.model('User',new mongoose.Schema({tenantId:{type:mongoose.Schema.Types.ObjectId,required:true,index:true},email:{type:String,required:true,unique:true,lowercase:true},passwordHash:{type:String,required:true}},opts));
export const Event=mongoose.model('Event',new mongoose.Schema({tenantId:{type:mongoose.Schema.Types.ObjectId,required:true,index:true},name:{type:String,required:true,trim:true},venue:{type:String,required:true,trim:true},startsAt:{type:Date,required:true},capacity:{type:Number,required:true,min:1,max:100000},status:{type:String,enum:['draft','open','closed'],default:'draft'}},opts));
const attendeeSchema=new mongoose.Schema({tenantId:{type:mongoose.Schema.Types.ObjectId,required:true,index:true},eventId:{type:mongoose.Schema.Types.ObjectId,required:true,ref:'Event'},name:{type:String,required:true,trim:true},email:{type:String,required:true,lowercase:true,trim:true},ticketType:{type:String,enum:['general','vip','staff'],default:'general'},checkedInAt:{type:Date,default:null}},opts);
attendeeSchema.index({tenantId:1,eventId:1,email:1},{unique:true});
export const Attendee=mongoose.model('Attendee',attendeeSchema);

