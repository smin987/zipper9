cask "zipper9" do
  version "1.0.0"
  sha256 :no_check

  url "https://github.com/smin987/zipper9/releases/download/v#{version}/zipper9-v#{version}-macos.dmg"
  name "zipper9"
  desc "Ultra-lightweight and high-speed multi-core archiver for Windows, Linux, and macOS"
  homepage "https://github.com/smin987/zipper9"

  auto_updates true
  depends_on macos: ">= :big_sur"

  app "zipper9.app"
  binary "#{appdir}/zipper9.app/Contents/MacOS/zipper9"

  zap trash: [
    "~/Library/Application Support/zipper9",
    "~/Library/Preferences/org.zipper9.app.plist",
    "~/.zipper9",
  ]
end
