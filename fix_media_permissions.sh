#!/bin/bash
# Fix media file permissions for nginx to serve them

# Make media directory readable and executable by others
chmod -R 755 media/

# Make all files in media directory readable by others
find media/ -type f -exec chmod 644 {} \;

# Make all directories in media readable and executable by others
find media/ -type d -exec chmod 755 {} \;

echo "Media permissions fixed. Nginx should now be able to serve media files."

