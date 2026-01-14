🧧Waring:
Created This for Personal Use and Turned it Into a Pip Package to be Able to Easily Use it on Other Computers, Don't Expect Great Quality or Updates




✨ Key Features
🎬 Video Generation: Create 9:16 or 16:9 videos with text, images, transitions, and background clips
🧠 AI Integration: Use OpenAI for text generation, formatting, and summaries
🌐 Web Automation: Automate browsers with Selenium for account creation, data scraping, and uploads
🧩 Stack Overflow Integration: Turn random Stack Overflow Q&A into narrated videos
🛡️ VPN & Proxy Management: Supports Tor, WireGuard, and random proxy rotation
🤖 Task Automation: Automatically enter giveaways, fill surveys, or post memes





🧩 Example Use Cases

🎬 1. create_info_video()

Generates and Uploads a complete Stack Overflow Q&A video automatically

BotingTools.create_info_video(
    driver,
    video_path="C:/Videos/StackOverflow/",
    img_folder="C:/Images/",
    clip1_path="assets/intro.mp4",
    img="assets/bg.png",
    clip2_path="assets/outro.mp4",
    font_path="assets/font.ttf"
)


📹 2. upload_video(driver, title)

Uploads a generated video to YouTube via Selenium automation.

BotingTools.upload_video(driver, "AI Explains Stack Overflow #42")


📦 3. create_youtube_meme((driver, img_path)

Creates a Random Meme Image and Uploads it to Youtube.

BotingTools.create_youtube_meme(
    driver,
    image_path="assets/meme.jpg",
)


🧰 4. create_rot_short(driver, rot_video_path)

Creates a TikTok-style “brainrot” short video with fast captions and meme audio.

BotingTools.create_brainrot_video(
    driver,
	rot_video_path ="C:/Videos/brainrot.mp4
)


🌐 5. connect_vpn(websites, index_file, vpn_folder, temp_file, temp_file_name)
Connects the system or Selenium browser to a VPN/proxy.

connect_vpn(
	websites = List of webstites the vpn shoul work on 
	index_file = Text File
	vpn_folder = Path Folder With Wireguard Config Files
	temp_file = Path to Wireguard Config File
	temp_file_name = Name of Temp Config File
)


💡 6. random_wait(min_s, max_s)

Pauses for a random delay (useful in web automation).

BotingTools.random_wait(2, 5)


🧠 7. start_driver(websites, index_file, vpn_folder, temp_file, temp_file_name, website_to_login, chrome_version, headless=0)
Create Driver Capable of Bypassing Cloudflare and HCapcha

	start_driver(
		websites, 
		index_file, 
		vpn_folder, 
		temp_file, 
		temp_file_name, 
		website_to_login = Website you want to use the driver with, 
		chrome_version = 137, 
		headless = 0
)


📊 8. create_account(email, driver, website_loged_in, name_path=None, email_path=None, Pass_path=None, conf_pass_path=None, sign_button1_path=None, sign_button2_path=None)
Automatically Create Any Account(Specifically Made to Create Multiple Accounts in Quick Succession)
Capable of Bypassing Cloudflare and HCapcha
	
create_account(
	email, 
	driver, 
	website_loged_in, 
	name_path = Xpath to username Field (optional), 
	email_path= Xpath to Email Field (optional), 
	Pass_path= Xpath to Password Field (optional), 
	conf_pass_path= Xpath to Confirm Password Field (optional), 
	sign_button1_path= Xpath to Button That Initiates Sign up Process Field (optional), 
	sign_button2_path= Xpath to Button That Concludes Sign up Process(optional)
)
	



⚙️ Installation

pip install BotingTools





📦 Dependencies

selenium	
moviepy	
pillow	
openai	
stackapi
requests
pydub	
ffmpeg