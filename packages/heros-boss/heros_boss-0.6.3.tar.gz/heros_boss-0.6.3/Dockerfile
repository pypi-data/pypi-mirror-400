# #########################################################################################
# Build image with everything required to run local and remote HEROS via BOSS
# #########################################################################################

FROM registry.gitlab.com/atomiq-project/heros

# Copy the contents of the repository into the image
WORKDIR /git
COPY . boss

# Install git for boss to be able to pull packages with pip from git
RUN apt-get update && apt-get install -y git

# Install BOSS in editable mode
RUN pip install --break-system-packages -e boss/
