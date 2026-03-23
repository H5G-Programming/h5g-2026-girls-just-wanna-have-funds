# 🌟 Your Friendly Guide to Coding! 🐍✨
Hey there, future coder! 👋

So you want to start coding? Amazing choice! This guide will walk you through setting up everything you need — your code editor, Python with uv, and Node.js with pnpm. Let's get you from zero to coding hero! 🦸‍♀️
---
## 🍺 Wait, What's Homebrew? (Mac Users!)
If you're on a Mac, there's a wonderful tool called Homebrew (or just brew). It's like an app store for your terminal — it lets you install developer tools with one simple command instead of hunting for download links on websites.

Installing Homebrew
Open your Terminal app (you can find it by pressing Cmd + Space and typing "Terminal") and paste this:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Follow the instructions on screen, and you're all set! Now you can install almost anything by typing brew install <something>. We'll use it a LOT in this guide. 🍏
---
## 🖥️ Get Yourself a Code Editor!
What's an IDE?
IDE stands for Integrated Development Environment. That sounds fancy, but it's really just a smart text editor made for writing code.

Think of it this way: you could write an essay in Notepad, right? But it's way nicer to use something like Google Docs that highlights your spelling mistakes, helps you format things, and keeps everything organized. An IDE does the same thing, but for code! It:

🎨 Colors your code so it's easier to read (this is called syntax highlighting)
🐛 Points out mistakes before you even run anything
▶️ Lets you run your code with one click
🧩 Suggests things as you type, like autocomplete on your phone
Why VS Code?
Visual Studio Code (VS Code for short) is one of the most popular IDEs in the world — and it's completely free! Millions of developers use it, from beginners to professionals. It's made by Microsoft and it works on Mac, Windows, and Linux.

Think of VS Code as your cozy creative workspace where all the magic happens. 🪄

Installing VS Code
On Mac (with Homebrew):

brew install --cask visual-studio-code
Done in one line! How satisfying is that? ✨

On Windows or if you prefer a manual install:

Go to code.visualstudio.com
Click the big Download button — it automatically picks the right version for your computer
Open the downloaded file and follow the installation steps
Launch VS Code and say hi to your new favorite app! 👋

Helpful Extensions
Once VS Code is open, let's give it some superpowers. Click the Extensions icon on the left sidebar (it looks like four little squares 🧩) and install these:

Search "Python" → Install the one by Microsoft 🐍
Search "ESLint" → Helps catch mistakes in JavaScript/TypeScript code
Search "Prettier" → Makes your code look neat and tidy automatically
---
## 🐍 Part 1: Python with uv
### 🤔 What Is uv?
Imagine you're baking cupcakes. You need:

The right oven (that's your Python version)
The right ingredients (those are called packages — little bits of code other people wrote that you can use!)
uv is like a magical kitchen helper that gets you the perfect oven AND all the ingredients you need, super fast! 🧁

### 🛠️ Installing uv
Open your terminal — you can do this right inside VS Code by going to Terminal → New Terminal in the menu!

On Mac (with Homebrew):

brew install uv
On Mac/Linux (without Homebrew):

curl -LsSf https://astral.sh/uv/install.sh | sh
On Windows (PowerShell):

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
That's it! You just installed your new best friend. 🎉

### 🐍 Getting a Python Version
You don't even need to go to a website to download Python. Just ask uv!

uv python install 3.12
Want to see which Python versions you have? Try:

uv python list
It's like browsing your wardrobe but for Python versions. 👗

🎒 Starting a New Python Project
Ready to start your first project? Let's say you're making something called "my-cool-app":

uv init my-cool-app
cd my-cool-app
This creates a neat little folder with everything set up for you. It's like getting a brand new notebook, already labeled and ready to go! 📓

Now open this folder in VS Code:

code .
(The . means "this folder". Neat, right?)

📂 Joining an Existing Project (There's Already a pyproject.toml!)
Sometimes you won't start a project from scratch — maybe a friend shared their project with you, or you downloaded one from GitHub. If you open the folder and see a file called pyproject.toml, that's great news! 🎉

This file is like a recipe card for the project. It lists which Python version is needed and which packages the project uses. You don't need to install anything one by one — just tell uv to read the recipe:

uv sync
That's literally it! One command and uv will:

🐍 Download the right Python version (if you don't have it yet)
📦 Install all the packages the project needs
✨ Set everything up so the project is ready to run
Then you can run the project the same way as always:

uv run python main.py
💡 Tip: Whenever you pull new changes from a shared project (like with git pull), it's a good habit to run uv sync again — just in case someone added new packages!

📦 Adding Packages (The Fun Ingredients!)
Packages are like superpowers for your code. Want to make a game? Analyze data? Draw charts? There's a package for that!

uv add requests
This installs a package called requests (it helps your code talk to the internet!).

Want a few more? Just keep adding:

uv add rich
uv add emoji
uv takes care of everything behind the scenes — no mess, no stress. 💅

▶️ Running Your Python Code
Write some Python in your project (the file is usually called main.py), then run it like this:

uv run python main.py
uv makes sure it uses the right Python version and all your packages. You just focus on the code!

🗑️ Removing a Package You Don't Need Anymore
Changed your mind about a package? No problem:

uv remove emoji
Gone! Clean and tidy. 🧹

🚀 Quick One-Off Scripts
Sometimes you just want to run a quick script without setting up a whole project. You can do this:

uv run --with rich python my_script.py
This temporarily grabs the rich package just for that one run. Super handy!
---
## 🟢 Part 2: JavaScript/TypeScript with Node.js and pnpm
Python isn't the only cool language out there! If you want to build websites, apps, or anything that runs in a browser, you'll want to learn JavaScript (or its fancier sibling TypeScript). For that, you need Node.js and a package manager called pnpm.

### 🤔 What Is Node.js?
Think of Node.js as the engine that lets you run JavaScript outside of a web browser. Normally JavaScript lives inside websites, but Node.js sets it free so you can use it to build all sorts of things — servers, tools, apps, you name it!

### 🤔 What Is pnpm?
Just like Python has packages, JavaScript has packages too (there are literally millions of them!). pnpm is a package manager that helps you install and manage them. It's like uv but for the JavaScript world!

Why pnpm instead of the default npm? Because pnpm is faster, uses less disk space, and keeps things cleaner. It's the cool upgraded version. 💜

### 🛠️ Installing Node.js
On Mac (with Homebrew):

brew install node
On Windows or Linux:

Go to nodejs.org
Download the LTS version (LTS stands for Long Term Support — it's the stable, reliable one)
Open the installer and follow the steps
Check that it worked by typing:

node --version
If you see a version number (like v22.x.x), you're golden! 🌟

This also installs npm (Node Package Manager) automatically. You can check that too:

npm --version
🛠️ Installing pnpm
Now let's install the better package manager!

On Mac (with Homebrew):

brew install pnpm
On any platform (using npm):

npm install -g pnpm
(The -g means "install it globally" — so you can use it from anywhere on your computer!)

Check it's installed:

pnpm --version
See a version number? You're all set! 🎉

🎒 Starting a New JavaScript/TypeScript Project
Let's create a new project:

mkdir my-awesome-site
cd my-awesome-site
pnpm init
This creates a package.json file — it's just like Python's pyproject.toml! It's the recipe card that keeps track of your project's name and all the packages it uses. 📋

Open it in VS Code:

code .
📂 Joining an Existing Project (There's Already a package.json!)
Just like with Python, sometimes you'll download or clone a project that already has everything listed in a package.json file. Just run:

pnpm install
And pnpm will fetch all the packages the project needs. Done! ✨

💡 Tip: Just like with uv sync, run pnpm install again after pulling new changes from Git!

📦 Adding JavaScript Packages
Want to add a package? Super easy:

pnpm add axios
This installs axios (a popular package for talking to the internet — similar to Python's requests!).

Need a package only for development (like a testing tool)? Add the -D flag:

pnpm add -D vitest
🗑️ Removing a JavaScript Package
Don't need a package anymore?

pnpm remove axios
Bye bye! 👋

▶️ Running Scripts
In JavaScript projects, you define commands in your package.json file under "scripts". For example, your package.json might look like this:

{
  "name": "my-awesome-site",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
Then you run them like this:

pnpm dev
or

pnpm build
It's like having little shortcuts for your most-used commands! 🏃‍♀️

💡 Handy Tips for Everything
uv is FAST. Like, really really fast. You'll notice. ⚡
pnpm is fast too — and it saves disk space by being clever about how it stores packages!
You don't need to worry about "virtual environments" for Python — uv handles that for you automatically!
If something goes wrong, uv help and pnpm help are always there for you.
In VS Code, press Ctrl + ** (or **Cmd + on Mac) to quickly open the terminal. You'll use this shortcut ALL the time!
The official docs are your friends:
uv → docs.astral.sh/uv
pnpm → pnpm.io
Node.js → nodejs.org/en/docs
🌈 You've Got This!
With your setup complete, you now have:

✅ Homebrew — your Mac app store for dev tools (if you're on Mac)
✅ VS Code — your cozy coding workspace
✅ Python + uv — for Python projects, data science, AI, and more
✅ Node.js + pnpm — for websites, apps, and everything JavaScript
That's a seriously powerful setup. Many professional developers use this exact combo every day — and now you have it too! 💪

Now go build something amazing — the world needs your ideas! 💖🐍🟢

Happy coding! 🎀