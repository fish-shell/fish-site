#!/usr/bin/env fish

function usage
  echo "Usage: deploy [stage|production]"
end

set -l BUCKET 's3://fishshell.com'
set -l SITE_URL 'http://fishshell.com.s3-website-us-east-1.amazonaws.com'

set -l production 0
if set -q argv[1]
  switch $argv[1]
    case stage
	  set production 0
	case production
	  set production 1
	case help -help --help -h
	  usage
	  exit 1
	case '*'
	  echo "Unknown option" $argv[1]
	  usage
	  exit 1
  end
end

if not test -d ./site
  echo "'site' directory not found"
  echo "Run from the top-level directory"
  exit 1
end

if [ production = 1 ]
  set SUFFIX ''
  echo "Syncing to PRODUCTION!"
else
  set SUFFIX staging
  echo "Syncing to staging"
end

aws s3 sync ./site $BUCKET/$SUFFIX --exclude .DS_Store --exclude files

echo Visit $SITE_URL/$SUFFIX

