const { createTransport } = require('nodemailer');
const { Client, Intents } = require('discord.js');
const { token } = require('./config.json');


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



// Login to Discord with your client's token
bot.login(token);




var sender = createTransport({
    service: 'gmail',
    auth: {
      user: 'smoothstocks1@gmail.com',
      pass: '!qazxsw23'
    }
  });



function send(email){

    var mailOptions = {
        from: 'smoothstocks1@gmail.com',
        to: email,
        subject: 'Welcome Email',
        text: 'Hello '+email.split('@')[0] +'!'
    };
      
    sender.sendMail(mailOptions, function(error, info){
        if (error) {
          console.log(error);
        } else {
          console.log('Email sent: ' + info.response);
        }
    });
}


function send_to(email){
  
  //var sender_email = document.getElementById("textbox")
  send(email)
  //s = sender_email.value.split('@')
 // if (s.length == 2){
  //  send(sender_email.value)
  //}
  //alert(sender_email.value)
}


send_to("tandavid2000@gmail.com")

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

