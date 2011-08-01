# usage/ watchr watchrc.rb

watch '^src/(.*)\.py$' do |match|
    pychecker match[0]
end

def pychecker file
  system("pychecker --stdlib #{file}") if File.exists?(file)
end
