from kivy.uix.accordion import NumericProperty, StringProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy import platform
from glob import glob
import asynckivy
import datetime
import cv2
import os
import itertools

def requestAccessToAllFiles():
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Environment = autoclass('android.os.Environment')
    Uri = autoclass('android.net.Uri')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    mActivity = PythonActivity.mActivity
    if not Environment.isExternalStorageManager(): # Checks if already Managing stroage
        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
        intent.setData(Uri.parse(f"package:{mActivity.getPackageName()}")) # package:package.domain.package.name
        mActivity.startActivity(intent)
		
from android.permissions import request_permissions, Permission

def request_storage_permissions():
    # Normal storage permissions
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE
    ])

request_storage_permisions()

requestAccessToAllFiles()

# '''Change this back before push'''
# Window.size = (400, 650)
# image_paths_all = glob('C:/Users/user/Desktop/my_folder/.Statuses/*.jpg')
# image_paths_saved = glob('C:/Users/user/Desktop/my_folder/Saved/Pics/*.jpg')
# video_paths_all = glob('C:/Users/user/Desktop/my_folder/.Statuses/*.mp4')
# video_paths_saved = glob('C:/Users/user/Desktop/my_folder/Saved/Vids/*.mp4')

# -----READ ME------- #
#Leave the above declaractions in the code since I need them to test the UI in my computer
#I only use the phone for small adjustments

### -----  TODO  ----- ###
#	Compile and test apk [done]
# 	Delete functionality for saved statuses [done]
# 	Open Whatsapp functionality
#	Fix the video screen errors

# --------END--------#
# add support for gbwhatsapp
image_paths_whatsapp = glob('/storage/emulated/0/Android/media/com.whatsapp/Whatsapp/Media/.Statuses/*.jpg')
image_paths_gbwhatsapp = glob('/storage/emulated/0/Android/media/com.gbwhatsapp/Whatsapp/Media/.Statuses/*.jpg') 
image_paths_saved = glob('/storage/emulated/0/Statuses/Pics/*.jpg')
video_paths_whatsapp = glob('/storage/emulated/0/Android/media/com.whatsapp/Whatsapp/Media/.Statuses/*.mp4')
video_paths_gbwhatsapp = glob('/storage/emulated/0/Android/media/com.gbwhatsapp/Whatsapp/Media/.Statuses/*.mp4')
video_paths_saved = glob('/storage/emulated/0/Statuses/Videos/*.mp4')

image_paths_all = list(itertools.chain(image_paths_whatsapp, image_paths_gbwhatsapp))
video_paths_all = list(itertools.chain(video_paths_whatsapp, video_paths_gbwhatsapp))



class Status:
    def __init__(self,file_type:str ="video", path:str = ''):
        self.ANDROID = glob("/storage/emulated/0/*")
        self.PICS = "/storage/emulated/0/Statuses/Pics"
        self.VIDS = "/storage/emulated/0/Statuses/Videos"
        self.types = ['video', 'pics']
        self.statuses_whatsapp = [i for i in glob('/storage/emulated/0/Android/media/com.whatsapp/Whatsapp/Media/.Statuses/*')]
        self.statuses_gbwhatsapp = [i for i in glob('/storage/emulated/0/Android/media/com.gbwhatsapp/Whatsapp/Media/.Statuses/*')]
        if path not in self.statuses_whatsapp or path not in self.statuses_gbwhatsapp:
            print(path)
            raise FileNotFoundError(f"{path} - File not found among  Whatsapp Statuses")
        try:
            if file_type in self.types:
                if file_type == "video":
                    n = self.VIDS
                elif (file_type == 'pics'):
                    n = self.PICS
                date_made = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                extension = os.path.splitext(path)[1]
                new_name = f"{date_made.strftime('%Y-%m-%d %H:%M:%S')}{extension}"
                new_file_path = os.path.join(n, new_name)
                with open(path, 'rb') as f:
                    video = f.read()
                with open(new_file_path, "wb") as f:
                    f.write(video)
            else:
                raise ValueError(f"{file_type} - Not known: valid values are 'video', 'pics'")
        except FileNotFoundError :
            if "/storage/emulated/0/Statuses" in self.ANDROID:
                print("Statuses folder Exists")
            else:
                print("Making Statuses Folder")
                os.makedirs("/sdcard/Statuses")
                os.makedirs("/sdcard/Statuses/Pics")
                os.makedirs("/sdcard/Statuses/Videos")
            Status(file_type, path)



class HomeScreen(Screen):

	def initialize_display(self):
		video_screen = self.manager.get_screen("video_screen")
		first_thumbnail = video_screen.generate_thumbnail(video_paths_all[0])
		self.ids['vid_backlay'].texture = first_thumbnail
		self.ids['img_backlay'].source = image_paths_all[0]

	def open_whatsapp(self):
		# ----------	Logic to open Whatsapp goes here	--------#
		os.system('am start -n com.whatsapp/com.whatsapp.HomeActivity')

	def change_screen(self, screen):
		self.manager.transition.direction = 'left'
		self.manager.transition.duration = .1
		self.manager.current = screen
		current_screen = self.manager.get_screen(screen)
		current_screen.change_content('all_tab')


class ImageScreen(Screen):
	loader = None
	
	async def async_load_images(self, image_list):
		content_grid = self.ids.layout
		content_grid.clear_widgets()
		for image in image_list:
			preview = ImageCard()
			img = Image(source=image, pos_hint={'center_x': .5, 'center_y': .5})
			preview.add_widget(img)
			Clock.schedule_once(lambda dt: content_grid.add_widget(preview))
			await asynckivy.sleep(0.2)  # Lets Kivy process events

	def change_content(self, tab):
		if self.loader:
			self.loader.cancel()
		content_grid = self.ids.layout
		content_grid.clear_widgets()
		global image_path
		if tab == 'all_tab':
			self.ids["all_tab_button"].state = "down"
			self.ids["saved_tab_button"].state = "normal"
			image_path = image_paths_all
		elif tab == 'saved_tab':
			self.ids["saved_tab_button"].state = "down"
			self.ids["all_tab_button"].state = "normal"
			image_path = image_paths_saved
		else:
			return
		# Start loading asynchronously
		self.loader = asynckivy.start(self.async_load_images(image_path))

	def expand(self, src):
		global image_view
		image_view.image_source = src
		image_view.open()
		global idx
		idx = image_path.index(src)


class VideoScreen(Screen):
	loader = None

	def generate_thumbnail(self, video, timestamp = .2):
		cap = cv2.VideoCapture(video)
		cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)		# Setting thumbnail to 'timestamp' seconds in.
		success, frame = cap.read()								# Getting frame data
		cap.release()
		if not success:
			return None
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
		height, width, _ = frame.shape
		buf = frame.tobytes()
		texture = Texture.create(size=(width, height), colorfmt='rgba')			# Create image texture
		texture.blit_buffer(buf, colorfmt = 'rgba', bufferfmt = 'ubyte')
		texture.flip_vertical()
		return texture

	async def async_load_thumbnails(self, video_list):
		content_grid = self.ids.vid_layout
		content_grid.clear_widgets()
		added_video_ids = set()				
		for index, video in enumerate(video_list):	
			video_id = index						
			if video_id in added_video_ids:			
				continue							
			thumbnail = Image(pos_hint={'center_x': .5, 'center_y': .5})
			texture = self.generate_thumbnail(video)
			if texture:
				thumbnail.texture = texture
			preview = VideoCard()
			preview.vid_src = video
			preview.add_widget(thumbnail)
			duplicate_found = False					
			for child in content_grid.children:
				if getattr(child, 'video_id', None) == video_id:
					duplicate_found = True
					break
			if not duplicate_found:
				content_grid.add_widget(preview)
				added_video_ids.add(video_id)  # Mark this video as added
			await asynckivy.sleep(0.1)  # Lets Kivy process events

	def change_content(self, tab):
		if self.loader:
			self.loader.cancel()
		global video_path
		content_grid = self.ids.vid_layout
		content_grid.clear_widgets()
		if tab == 'all_tab':
			self.ids["all_tab_button"].state = "down"
			self.ids["saved_tab_button"].state = "normal"
			video_path = video_paths_all
		elif tab == 'saved_tab':
			self.ids["saved_tab_button"].state = "down"
			self.ids["all_tab_button"].state = "normal"
			video_path = video_paths_saved
		else:
			return
		# Start loading asynchronously
		self.loader = asynckivy.start(self.async_load_thumbnails(video_path))

	def expand(self, src):
		global video_view
		if video_view.video_source != src:
			video_view.video_source = src  # Change source only if needed
		video_view.open()
		global idx
		idx = video_path.index(src)



class VideoPopup(ModalView):
	video_source = StringProperty()
	is_saved = BooleanProperty()
	progress = NumericProperty(0)
	start_time = 1

	def __init__(self, **kwargs):
		super(VideoPopup, self).__init__(**kwargs)
		self.bind(on_open=self._bind_video)
		self.bind(on_pre_dismiss=self._close_video)
		self.video_length = 1

	def on_pre_open(self):
		super().on_pre_open()
		self.on_source()

	def on_source(self):
		with open(self.video_source, 'rb') as vid_data_src:
			vid_data = vid_data_src.read()
		for i in video_paths_saved:
			with open(i, 'rb') as k:
				saved_vid_data = k.read()
			if saved_vid_data == vid_data:
				self.is_saved = True
				return
		self.is_saved = False

	def _bind_video(self, *args):
		video = self.ids.video
		video.load_first = True
		video.state = "play"
		video.bind(on_duration = self.update_duration)
		video.bind(on_position = self.update_progress)
		Clock.schedule_interval(self.update_progress_bar, .1)
	
	def _close_video(self, *args):
		video = self.ids.video
		if video.state == 'play':
			video.state == 'stop'
		video.load_first = True
		video.unload()

	def update_duration(self, instance, value):
		self.video_length = value if value > 0 else 1

	def update_progress(self, instance, value):
		self.progress = (value / self.video_length) * 100

	def update_progress_bar(self, dt):
		video = self.ids.video
		if video.duration > 0:
			self.progress = (video.position / video.duration) * 100
		if self.progress >= 98:
			self.ids.video._on_eos()

	def play_pause(self):
		video = self.ids.video
		if video.state == 'play':
			video.state = 'pause'
		else:
			video.state = 'play'
	
	def play_next(self):
		global idx
		idx += 1
		if idx >= len(video_path):
			idx = len(video_path)-1
		self.video_source = video_path[idx]
		self.load_first = False
		self.ids.video.state = 'play'
		self.on_source()

	def play_previous(self):
		global idx
		idx -= 1
		if idx < 0:
			idx = 0
		self.video_source = video_path[idx]
		self.load_first = False
		self.ids.video.state = 'play'
		self.on_source()

	def save_delete_video(self):
		if self.ids['save_delete_icon'].icon == 'download':
			Status(file_type="video", path=self.video_source)
			global video_paths_saved
			video_paths_saved = glob('/storage/emulated/0/Statuses/Videos/*.mp4')
		elif self.ids['save_delete_icon'].icon == 'delete-empty':
			target_path = None
			if self.ids['save_delete_icon'].icon == 'download':
				viewed_vid_size = os.path.getsize(self.video_source)
				for saved_path in video_paths_saved:
					if os.path.getsize(saved_path) == viewed_vid_size:
						with open(saved_path, 'rb') as vs, open(self.video_source, 'rb') as source_vid:
							if vs.read() == source_vid.read():
								target_path = saved_path
								break
			if target_path:
				os.remove(target_path)



class ImageViewer(ModalView):
	image_source = StringProperty()
	is_saved = BooleanProperty()
	
	def on_pre_open(self):
		super().on_pre_open()
		self.on_source()

	def on_source(self):
		with open(self.image_source, 'rb') as img_data_src:
			img_data = img_data_src.read()
		for i in image_paths_saved:
			with open(i, 'rb') as k:
				saved_img_data = k.read()
			if saved_img_data == img_data:
				self.is_saved = True
				return
		self.is_saved = False

	def contract(self):
		self.dismiss()

	def next_img(self):
		global idx
		idx += 1
		if idx >= len(image_path):
			idx = len(image_path)-1
		self.image_source = image_path[idx]
		self.on_source()

	def prev_img(self):
		global idx
		idx -= 1
		if idx < 0:
			idx = 0
		self.image_source = image_path[idx]
		self.on_source()

	def save_delete_img(self):
		if self.ids['save_delete_icon'].icon == 'download':
			Status(file_type="pics", path=self.image_source)
			global image_paths_saved
			image_paths_saved = glob('/storage/emulated/0/Statuses/Pics/*.jpg')
		elif self.ids['save_delete_icon'].icon == 'delete-empty':
			if os.path.exists(self.image_source):
				os.remove(self.image_source)



class StatusVideo(Video):
	load_first = True

	def _on_load(self, *largs):
		super()._on_load(*largs)
		self.seek(.001)
		if self.load_first:
			self.state = 'pause'
			self.load_first = False

	def _on_eos(self, *largs):
		super()._on_eos(*largs)
		self.parent.parent.play_next()



class ImageCard(MDCard):
	pass


class VideoCard(MDCard):
	vid_src = StringProperty()



class StatusSaverApp(MDApp):

	def build(self):
		Builder.load_file('main.kv')
		Window.clearcolor = (1, 1, 1, 1)
		my_manager = ScreenManager()
		home_screen = HomeScreen(name = 'home')
		image_screen = ImageScreen(name = 'image_screen')
		video_screen = VideoScreen(name = 'video_screen')
		global image_view
		global video_view
		image_view = ImageViewer()
		video_view = VideoPopup()
		my_manager.add_widget(image_screen)
		my_manager.add_widget(video_screen)
		my_manager.add_widget(home_screen)
		home_screen.initialize_display()
		my_manager.current = 'home'
		return my_manager



if __name__ == '__main__':
	StatusSaverApp().run()
