# Base image to expand
FROM registry.gitlab.com/atomiq-project/herosdevices

# Copy the vendor library into the container
COPY pvcam /pvcam

# Install prerequisites
RUN apt-get update && apt-get install -y sudo git

# Install the vendor library itself
# We have to agree to some licenses here so we use the "yes" command.
# The EUID=1 is a little hack to trick the installer into thinking we're not root.
RUN yes | EUID=1 /bin/bash /pvcam/pvcam__install_helper-Ubuntu.sh

# Remove build files after installation to make image a bit smaller
RUN rm -rf /pvcam

# We need to point the python api to the correct library path
ENV PVCAM_SDK_PATH="/opt/pvcam/sdk"
# Install python API
RUN pip install --break-system-packages PyVCAM

