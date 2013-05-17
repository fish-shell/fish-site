require 'formula'

class Fish < Formula
  homepage 'http://fishshell.com'
  url 'http://fishshell.com/files/2.0.0/fish.tar.gz'
  sha1 'af99e58360a1fcb3ecb6b324d99757fda504c164'
  version '2.0.0'

  head 'git://github.com/fish-shell/fish-shell.git'

  # Indeed, the head build always builds documentation
  depends_on 'doxygen' => :build if build.head?
  depends_on :autoconf

  skip_clean 'share/doc'

  conflicts_with "fishfish"

  def install
    system "autoconf"
    system "./configure", "--prefix=#{prefix}"
    system "make install"
  end

  def caveats; <<-EOS.undent
    You will need to add:
      #{HOMEBREW_PREFIX}/bin/fish
    to /etc/shells. Run:
      chsh -s #{HOMEBREW_PREFIX}/bin/fish
    to make fish your default shell.
    EOS
  end
end
