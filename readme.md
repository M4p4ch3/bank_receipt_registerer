# Bank Receipt Registerer

***Android application to register bank operations***

## Build and run from source

### Requirements

- Python :

  ```sh
  sudo apt-get install python3 python3.10-venv

  # Add to ~/.bashrc
  alias python=python3

  # Venv recommended
  python -m venv kivy_venv
  source kivy_venv/bin/activate
  ```

- [kivy](https://kivy.org/doc/stable/gettingstarted/installation.html) :

  ```sh
  pip install kivy
  ```

- [buildozer](https://buildozer.readthedocs.io/en/latest/installation.html) :

  ```sh
  sudo apt-get install zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

  # Issue with setuptools higher than 58
  pip install setuptools==58.0.0 wheel Cython==0.29.33 buildozer

  # Add to ~/.bashrc
  export PATH=$PATH:~/.local/bin/
  ```

- (optional) ADB, for debug :

  ```sh
  sudo apt-get install adb
  ```

### Setup

Create `buildozer.spec` :

```sh
buildozer init
```

Edit `buildozer.spec` :

```conf
requirements = python3==3.9.9,hostpython3==3.9.9,setuptools==58.0.0,kivy,android
```

```conf
# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path = /media/pache/Data1/Home/tech/dev/android/ndk

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
android.sdk_path = /media/pache/Data1/Home/tech/dev/android/sdk

# (str) ANT directory (if empty, it will be automatically downloaded.)
android.ant_path = /media/pache/Data1/Home/tech/dev/android/ant
```

### Build

```sh
buildozer android debug
```

### Deploy

```sh
buildozer deploy run
```

### Debug

```sh
adb logcat
```
