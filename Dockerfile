FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    bzip2 \
    git \
    sudo \
    adduser \
    bash \
    vim \
    nano \
    passwd \
    ca-certificates \
    build-essential \
    libpam0g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
ENV CONDA_DIR=/opt/conda
ENV PATH="$CONDA_DIR/bin:$PATH"
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    conda clean -afy

# Create conda base environment and install packages
RUN conda install -y -c conda-forge \
    pip \
    jupyterhub \
    jupyterlab \
    notebook \
    ipykernel \
    jupyterlab-git \
    pamela \
    && conda clean --all --yes

# Install NativeAuthenticator
RUN pip install git+https://github.com/jupyterhub/nativeauthenticator.git

# Create 'ofs' environment from YAML
COPY envs/ofs_env.yml /tmp/ofs_env.yml
RUN conda env create -f /tmp/ofs_env.yml

# Register 'ofs' kernel
RUN /opt/conda/envs/ofs/bin/python -m ipykernel install --prefix=/opt/conda --name ofs --display-name "Python (OFS)"

# Activate ofs environment automatically in terminals
RUN echo "source /opt/conda/etc/profile.d/conda.sh" > /etc/profile.d/conda-init.sh && \
    echo "conda activate ofs" >> /etc/profile.d/conda-init.sh && \
    chmod +x /etc/profile.d/conda-init.sh

# Lock down /opt/conda for root-only install
RUN chown -R root:root /opt/conda && \
    chmod -R go-w /opt/conda
#     find /opt/conda -type d -exec chmod 755 {} \; && \
#     find /opt/conda -type f -exec chmod 644 {} \;

# Prevent per-user install and override
RUN mkdir -p /etc/skel && \
    echo "alias conda='echo ❌ Conda install is restricted to admin only.'" >> /etc/skel/.bashrc && \
    echo "alias micromamba='echo ❌ Micromamba install is restricted to admin only.'" >> /etc/skel/.bashrc && \
    echo "export CONDA_ENVS_PATH=/opt/conda/envs" >> /etc/skel/.bashrc && \
    echo "export CONDA_PKGS_DIRS=/opt/conda/pkgs" >> /etc/skel/.bashrc

# Copy user creation script and training files
COPY create_users.py /usr/local/bin/create_users.py
COPY user_credentials.txt /tmp/user_credentials.txt
COPY templates/ /opt/template/
RUN chmod -R 755 /opt/template

# Clone training materials
RUN git clone https://github.com/devmetmar/marinemet-training.git /opt/marinemet-training || echo "Clone failed"

# Copy JupyterHub config
COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

# Set root password
RUN echo "root:admin123" | chpasswd

# Start JupyterHub and create users
CMD ["bash", "-c", "python /usr/local/bin/create_users.py && jupyterhub --ip=0.0.0.0 --port=8000 --config=/srv/jupyterhub/jupyterhub_config.py"]
