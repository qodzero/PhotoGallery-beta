from kivy.config import Config
from kivy.core.window import Window

# Config.set('graphics','fullscreen','auto')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty
from kivy.graphics import *

from kivy.loader import Loader

from kivy.garden.iconfonts import *
import os
from os.path import join, dirname
from PIL import Image as pillow
from PIL import ImageFilter


class ExtendedImg(ButtonBehavior, Image):
    pass

class ViewImage(ModalView):
    pass

class CropBounds(ModalView):

    def __init__(self, **kwargs):
        super(CropBounds, self).__init__(**kwargs)
        self.to_crop = True
        print('Center: ',self.center)
        print('Size: ',self.size)
        print('Window Width: ',Window.width)
        print('Window Height: ',Window.height)
        


    def on_touch_down(self, touch):
        self.canvas.clear()
        
        if self.collide_point(*touch.pos) and self.to_crop:
            with self.canvas:
                        
                        self.start_x = touch.x
                        self.start_y = touch.y
                        touch.ud['area'] = Line(points=(touch.x, touch.y, touch.x, 400,touch.x, touch.y,touch.x, touch.y, touch.x, touch.y))
                        print("Pos: ",touch.pos)
            return True
        # push the current coordinate, to be able to restore it later

        # dispatch the touch as usual to children
        # the coordinate in the touch is now in local space


        return GalleryWindow().on_touch_down(touch)

    def on_touch_move(self,touch):
        if self.collide_point(*touch.pos) and self.to_crop:
            touch.ud['area'].points = (self.start_x, self.start_y, self.start_x, touch.y, touch.x, touch.y, touch.x, self.start_y, self.start_x, self.start_y)

            return True
        return GalleryWindow().on_touch_down(touch)
    def on_touch_up(self,touch): 
        # crop image using the coordinates given by the <on_touch_down> and <on_touch_move> events
        if self.collide_point(*touch.pos) and self.to_crop:

            image_base = None
            #find image container
            for child in self.parent.children:
                if str(child).find('ViewImage') > -1:
                    image_base = child

            if image_base != None:
                img_parent = None
                for ip in image_base.children:
                    if str(ip).find('BoxLayout') > -1:
                        img_parent = ip
                        target = img_parent.children[0]
                        # print(target.source)
                        im = pillow.open(target.source)

                        crop_bounds = (self.start_x,self.start_y,touch.x,touch.y)
                        print(crop_bounds)
                        # cropped_img = im.crop(crop_bounds)
                        # img_name = target.source[:-4]
                        # save_name = 'cropped.png'
                        # print(save_name)
                        # cropped_img.save(save_name)
                        # # target.source = cropped_img



            #Make sure these on_touch_* functions are only called when we are actually cropping
            self.to_crop = False
            return True
        return GalleryWindow().on_touch_down(touch )           

class GalleryWindow(BoxLayout):
    def __init__(self, **kwargs):
        super(GalleryWindow, self).__init__(**kwargs)
        # img_back = 'img/57seWkK.jpg'
        self.float_layout = FloatLayout(size=(self.size))
        self.img_view = GridLayout(cols=4,spacing=5,padding=20,size_hint_y=None)
        self.img_view.bind(minimum_height=self.img_view.setter('height'))
        self.floor = ScrollView(size_hint=(1, None), size=(Window.width-20, Window.height-120),bar_color=(1,1,1, 1),bar_inactive_color=(1,1,1, .4),bar_width=5,scroll_type=['bars'])
        self.add_widget(self.floor)
        self.floor.add_widget(self.img_view)
        self.images = self.img_grabber('img')
        self.show_imgs()

    # def img_cont_size(self):
    #     im_width = (Window.width-40)/4
    #     im_height = (Window.height-50)/4
    def show_imgs(self):
        self.images = self.img_grabber('img')
        if len(self.images) > 0:
            for img in sorted(self.images):
                im_width = 300
                im_height = 250
                # im_height = NumericProperty(0)
                # im_width = NumericProperty(0)
                # im_width = (Window.width-40)/4
                # im_height = (Window.height-50)/4
                # im_width.bind()
                img_container = BoxLayout(size_hint=(.33,None),size=(im_width,im_height),orientation='vertical')
                # img_container.bind(size=self._size)
                img_path = 'img/'+img
                image = ExtendedImg(source=img_path,on_release=self.show_full_img)
                
                caption = Button(text=img[:20],size_hint=img_container.size_hint,size=(im_width,30),background_normal='',background_color=(0,0,0, .5))
                
                img_container.add_widget(image)
                img_container.add_widget(caption)
                self.img_view.add_widget(img_container)

    if Window.on_resize:
        print('Resized!!!!')
    def show_full_img(self, instance):
        
        clicked_img = instance.source
        img = Image(source=clicked_img)
        img_size_x = img.texture_size[0]
        img_size_y = img.texture_size[1]

        #Normalise the image width
        while img_size_x >= Window.width or img_size_y >= Window.height:
            if img_size_x > img_size_y:
                img_size_x -= 16
                img_size_y -= 9
            else:
                img_size_y -= 9
        
        img_size_x - 100
        img_size_y - 100
        #Normalise the image height
        # while img_size_y > Window.height - 90:
        #     img_size_y -= 9

        #Get the next and previous images
        all_imgs = sorted(self.images)
        print('Image Size: (%sx%s)'%(img_size_x,img_size_y))
        print('Image Center: ',img.center)
        print('Img Position: ',img.pos)
        nxt_img = 'img/'
        prev_img = 'img/'
        for x in range(len(all_imgs)):
            if all_imgs[x] == clicked_img[4:]:
                if x != len(all_imgs)-1:
                    nxt_img += all_imgs[x+1]
                else:
                    nxt_img = all_imgs[0]
                if x != 0:
                    prev_img += all_imgs[x-1]
                else:
                    prev_img += all_imgs[len(all_imgs)-1]
                break

        view_image = ViewImage(size_hint=(None, None),size=(img_size_x, img_size_y),padding=(0,0),background_color=(0,0,0, .8))
        print('Modal Size: ',view_image.size)
        print('Modal Center: ',view_image.center)
        print('Window Size: (%sx%s)'%(Window.width,Window.height))
        print('Window Center: (%sx%s)'%(Window.width/2,Window.height/2))
        with view_image.canvas.before:
            Color(1,1,1,.8)
            Rectangle(source=instance.source,pos=self.pos,size=self.size)
        image_container = BoxLayout(spacing=10,padding=(0,10))
        image_ops = AnchorLayout(anchor_x= 'center',anchor_y='bottom')
        image_ops_cont = BoxLayout(size_hint=(None,None), size=(200,50))

        prev_img_btn = Button(text='%s'%(icon('zmdi-caret-left',32)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(95,30),background_normal='',background_color=(1,1,1, .5))

        nxt_img_btn = Button(text='%s'%(icon('zmdi-caret-right',26)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(95,30),background_normal='',background_color=(1,1,1, .5))

        crop = Button(text='%s'%(icon('zmdi-crop',26)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(45,30),background_normal='',background_color=(1,1,1, .5),on_release=self.crop_image)

        set_as = Button(text='%s'%(icon('zmdi-wallpaper',26)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(45,30),background_normal='',background_color=(1,1,1, .5))

        effects = DropDown()
        effect_sharpen = Button(text='%s'%(icon('zmdi-grain',32)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(45,30),background_normal='',background_color=(1,1,1, .5),on_release=self.sharpen_image)
        effect_blur = Button(text='%s'%(icon('zmdi-blur',32)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(45,30),background_normal='',background_color=(1,1,1, .5),on_release=self.blur_image)
        effect_emboss = Button(text='%s'%(icon('zmdi-gradient',32)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(45,30),background_normal='',background_color=(1,1,1, .5),on_release=self.emboss_image)
        effect_cartoon = Button(text='%s'%(icon('zmdi-exposure',32)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(45,30),background_normal='',background_color=(1,1,1, .5),on_release=self.cartoon_image)

        #Add Effects Buttons To The Dropdown
        effects.add_widget(effect_sharpen)
        effects.add_widget(effect_blur)
        effects.add_widget(effect_emboss)
        effects.add_widget(effect_cartoon)

        effects_list_trigger = Button(text='%s'%(icon('zmdi-graphic-eq',32)),color=(0,0,0,1),markup=True,size_hint=(None,None),size=(45,30),background_normal='',background_color=(1,1,1, .5),on_release=effects.open)

        image_ops_cont = BoxLayout(size_hint=(None,None), size=(200,50))

        #Add image operations buttons to their container
        image_ops_cont.add_widget(prev_img_btn)
        image_ops_cont.add_widget(crop)
        image_ops_cont.add_widget(set_as)
        image_ops_cont.add_widget(effects_list_trigger)
        image_ops.add_widget(image_ops_cont)
        image_container.add_widget(img)
        image_ops_cont.add_widget(nxt_img_btn)
        
        #Display all widgets to the screen
        view_image.add_widget(image_container)
        view_image.add_widget(image_ops)
        view_image.open()
        # print('Children: \n',view_image.parent.children)

    #Sharpen Image
    def sharpen_image(self,instance):

        #Get the image to be cropped
        img_container_parent = instance.parent.parent.parent
        img_container = img_container_parent.children[1]
        for child in img_container.children:
            if str(child).find('BoxLayout') > -1:
                target_img = child.children[0]
    
        
        im = pillow.open(target_img.source)
        sharpr = im.filter(ImageFilter.UnsharpMask(radius=20))
        im_name = im.filename[:-4]+'_sharp'+im.filename[-4:]
        sharpr.save(im_name)
        self.img_view.clear_widgets()
        self.show_imgs()
        target_img.source = im_name

    #Emboss Image
    def emboss_image(self,instance):

        #Get the image to be cropped
        img_container_parent = instance.parent.parent.parent
        img_container = img_container_parent.children[1]
        for child in img_container.children:
            if str(child).find('BoxLayout') > -1:
                target_img = child.children[0]
    
        
        im = pillow.open(target_img.source)
        emboss = im.filter(ImageFilter.EMBOSS)
        im_name = im.filename[:-4]+'_emboss'+im.filename[-4:]
        emboss.save(im_name)
        self.img_view.clear_widgets()
        self.show_imgs()
        target_img.source = im_name

    #Blur Image
    def blur_image(self,instance):

        #Get the image to be cropped
        img_container_parent = instance.parent.parent.parent
        img_container = img_container_parent.children[1]
        for child in img_container.children:
            if str(child).find('BoxLayout') > -1:
                target_img = child.children[0]
    
        
        im = pillow.open(target_img.source)
        gaussian = im.filter(ImageFilter.GaussianBlur(radius=20))
        im_name = im.filename[:-4]+'_blur'+im.filename[-4:]
        gaussian.save(im_name)
        self.img_view.clear_widgets()
        self.show_imgs()
        target_img.source = im_name

    #Sharpen Image
    def cartoon_image(self,instance):

        #Get the image to be cropped
        img_container_parent = instance.parent.parent.parent
        img_container = img_container_parent.children[1]
        for child in img_container.children:
            if str(child).find('BoxLayout') > -1:
                target_img = child.children[0]
    
        
        im = pillow.open(target_img.source)
        cartoon = im.filter(ImageFilter.EDGE_ENHANCE)
        im_name = im.filename[:-4]+'_toon'+im.filename[-4:]
        cartoon.save(im_name)
        self.img_view.clear_widgets()
        self.show_imgs()
        target_img.source = im_name

    def crop_image(self,instance):

        #Get the image to be cropped
        img_container_parent = instance.parent.parent.parent
        img_container = img_container_parent.children[1]
        target_img = img_container.children[0]
        img_size = img_container_parent.size #get the image's size
        img_size_x = img_size[0]
        img_size_y = img_size[1]
        
        crop_overlay = CropBounds(size_hint=(None, None),size=(img_size_x, img_size_y),padding=(0,0),background_color=[0,0,0, .3],opacity=.5,attach_to=target_img)

        with crop_overlay.canvas.before:
                Color(1,1,1,1)
                # Rectangle(pos=self.pos,size=self.size)
        
        crop_overlay.open()





    def close(self):
        Window.close()
    def img_grabber(self,path):
        if not os.path.exists(path):
            print('Path Not Found')
        else:
            imgs = []
            #get the images down here
            files = os.listdir(path)
            for f in files:
                if f.endswith('.png') or f.endswith('.jpg'):
                    imgs.append(f)
            
        return imgs

    def set_wallpaper(self):
        command = '''dbus-send --session --dest=org.kde.plasmashell --type=method_call /PlasmaShell org.kde.PlasmaShell.evaluateScript "string:
        var Desktops = desktops();
        for (i=0;i<Desktops.length;i++){
            d =Desktops[i];
            d.wallpaperPlugin = 'org.kde.image';
            d.currentConfigGroup = Array('Wallpaper','org.kde.image','General');
            d.writeConfig('Image','file:///')
        }'''

class GalleryApp(App):
    
    def on_load(self):
        print('App Started!!!')

    def build(self):
        return GalleryWindow()

if __name__=="__main__":
    register('default_font', './assets/fonts/Material-Design-Iconic-Font.ttf',
             join(dirname(__file__), 'assets/fonts/zmd.fontd'))

    gallery_app = GalleryApp()
    gallery_app.run()
