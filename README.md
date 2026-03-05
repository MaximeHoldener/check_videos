# 📺 Daily YouTube Video Checker

Automatically checks your YouTube subscriptions for new videos every day and generates an HTML page you can access from anywhere, including your iPhone!

## 🌐 Access Your Videos

Once set up, your new videos will be available at:
```
https://YOUR_GITHUB_USERNAME.github.io/YOUR_REPOSITORY_NAME/
```

Simply bookmark this URL on your iPhone for instant access! 📱

## 🚀 Setup Instructions

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in (or create an account)
2. Click the **+** button in the top right → **New repository**
3. Name it (e.g., `youtube-checker`)
4. Make it **Public** (required for free GitHub Pages)
5. Click **Create repository**

### 2. Upload Your Files

1. On your computer, open Terminal
2. Navigate to this folder:
   ```bash
   cd /Users/maxime/Desktop/youtube_script/second_try
   ```

3. Initialize git and push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - YouTube video checker"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
   
   Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name.

### 3. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under **Source**, you'll see it's being deployed from `gh-pages` branch (this will be created automatically by the workflow)

### 4. Enable GitHub Actions

1. In your repository, click **Actions** (top menu)
2. Click **I understand my workflows, enable them**
3. The workflow will run automatically every day at 8:00 AM UTC

### 5. Test It Now (Manual Run)

1. Go to **Actions** tab
2. Click **Daily YouTube Video Check** (left sidebar)
3. Click **Run workflow** → **Run workflow**
4. Wait ~1-2 minutes for it to complete
5. Visit `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`

## ⏰ Schedule

The script runs automatically every day at **8:00 AM UTC**. 

To change the time, edit [.github/workflows/daily-video-check.yml](.github/workflows/daily-video-check.yml):
```yaml
- cron: '0 8 * * *'  # Change '8' to your preferred hour (0-23)
```

Time zone reference:
- 8:00 AM UTC = 12:00 AM (midnight) PST / 3:00 AM EST
- 16:00 (4 PM) UTC = 8:00 AM PST / 11:00 AM EST

## 📱 iPhone Shortcuts

### Create a Home Screen Bookmark:

1. Open Safari on your iPhone
2. Go to `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`
3. Tap the Share button (square with arrow)
4. Tap **Add to Home Screen**
5. Name it "New YouTube Videos" 🎉

### Create an iOS Shortcut (Optional):

1. Open the Shortcuts app
2. Create a new shortcut
3. Add action: **Open URLs**
4. Enter your GitHub Pages URL
5. Add to home screen or run from widget

## 📂 Files Overview

- **newVideos.py** - Main script that checks for new videos
- **output_valid_only.csv** - Your YouTube channel subscriptions
- **.github/workflows/daily-video-check.yml** - Automation configuration
- **docs/** - Where the HTML page is generated for GitHub Pages
- **requirements.txt** - Python dependencies

## 🔧 How It Works

1. **GitHub Actions** runs the script every day automatically
2. The script checks all your YouTube subscriptions for new videos
3. Generates `new_videos.html` with all new videos
4. Deploys the HTML to **GitHub Pages** (publicly accessible)
5. You access the page from your iPhone's browser! 📱

## 🆘 Troubleshooting

**Q: The page shows a 404 error**
- Wait 2-3 minutes after the first workflow run
- Check that your repository is Public
- Verify GitHub Pages is enabled in Settings → Pages

**Q: No new videos appear**
- The script compares against the last stored URLs
- New videos only appear if they're different from what's stored
- Try running manually to test: Actions → Run workflow

**Q: Want to check more frequently?**
- Edit the cron schedule in the workflow file
- Note: GitHub Actions has usage limits on free accounts

**Q: How do I add/remove channels?**
- Edit `output_valid_only.csv` or `abonnements.csv`
- The CSV format is: Channel, xmlUrl, LastVideo, LastUrl

## 📊 What Gets Updated

Every time the script runs:
- ✅ Checks all channels for new videos
- ✅ Updates `output_valid_only.csv` with latest videos
- ✅ Creates `new_videos.html` with new videos found
- ✅ Creates `new_videos.csv` with the raw data
- ✅ Commits changes back to the repository
- ✅ Deploys updated page to GitHub Pages

## 🎯 Next Steps

1. Follow the setup instructions above
2. Test the manual workflow run
3. Bookmark the page on your iPhone
4. Enjoy automated daily YouTube video updates! 🎉

---

**Need help?** Check the workflow logs in the Actions tab or create an issue in the repository.
