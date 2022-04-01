const { createTransport } = require('nodemailer');
const { Client, Intents } = require('discord.js');
const { token } = require('./config.json');

user_one = {
  'email':'tandavid2000@gmail.com',
  'discord':'abanana',
  'follow_stocks':'meta'
}

user_two = {
  'email':'dtan2@buffalo.edu',
  'discord':'UnderSoul',
  'follow_stocks':'AMC'
}

arr_users = [user_one, user_two]

arr_test = ['meta', 'AMC']

stocks_db_local = {
  'meta':185,
  'appl':150,
  'AMC':15,
  'GME':88
}

const intents = ["GUILDS", "GUILD_MEMBERS", "GUILD_MESSAGES"];


// Create a new client instance
const bot = new Client({intents: intents});


// When the client is ready, run this code (only once)
bot.once('ready', () => {
	console.log('Ready!');
  bot.channels.cache.get("404773877042905100").send(`I'm online!`)
  
});


bot.on('guildMemberAdd', (member) => {
	console.log(member.user.tag);
  bot.channels.cache.get("404773877042905100").send(`Hello `+'@'+member.user.tag)
  
});

bot.on("price_change", (stock, member) => {

  bot.channels.cache.get("404773877042905100").send('@'+member+" The stock "+stock+" price has change more than 5% today")

});


// Login to Discord with your client's token
bot.login(token);




var sender = createTransport({
    service: 'gmail',
    auth: {
      user: 'smoothstocks1@gmail.com',
      pass: '!qazxsw23'
    }
  });



function send(email, message){

    var mailOptions = {
        from: 'smoothstocks1@gmail.com',
        to: email,
        subject: 'Welcome Email',
        text: message
    };
      
    sender.sendMail(mailOptions, function(error, info){
        if (error) {
          console.log(error);
        } else {
          console.log('Email sent: ' + info.response);
        }
    });
}


function send_to(email, message){
  
  //var sender_email = document.getElementById("textbox")
  send(email, message)
  //s = sender_email.value.split('@')
 // if (s.length == 2){
  //  send(sender_email.value)
  //}
  //alert(sender_email.value)
}

notify = 5

function change_notify(){
  
  //var sender_email = document.getElementById("textbox")
  notify = parseInt(document.getElementById("textbox").value)
  
  //s = sender_email.value.split('@')
 // if (s.length == 2){
  //  send(sender_email.value)
  //}
  //alert(sender_email.value)
}

function confirm(){
				
  test = "https://discord.com/api/webhooks/950491418491752448/ZKjXE4laBmFGZxbls5cpZhZ3lbqiO8DXR6S9UweEQ_uowDXeh2kBmnflT9nQh6sJq47K"
  const request = new XMLHttpRequest();
  request.open("POST", test);
  
  request.setRequestHeader('Content-type', 'application/json');

  

  request.send(JSON.stringify(params = {
    username: "My Webhook Name",
    avatar_url: "",
    content: "Welcome"
    }));
}

const delay = ms => new Promise(res => setTimeout(res, ms));


function simulate(){
  setTimeout(function (){
    ran = Math.random()
    change = Math.floor(Math.random() * Math.floor(Math.random() * 10))
    r_idx = Math.floor(Math.random() * arr_test.length)

    if(ran > 0.5){
      stocks_db_local[arr_test[r_idx]] += change
    }else{
      stocks_db_local[arr_test[r_idx]] -= change
    }


    console.log(arr_test[r_idx]+" "+stocks_db_local[arr_test[r_idx]].toString())
    if (parseFloat(change)/parseFloat(stocks_db_local[arr_test[r_idx]]) >= (notify/100)){
      for(var i=0; i<arr_users.length; i++){
        if (arr_users[i]['follow_stocks'] == arr_test[r_idx]){
          send_to(arr_users[i]["email"], "price change greater than 5%")
          bot.emit("price_change", arr_test[r_idx], arr_users[i]["discord"])

        }
      }
    }

    simulate()
  }, 5000)}





simulate()