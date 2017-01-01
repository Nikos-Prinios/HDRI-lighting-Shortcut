# HDRI-lighting-Shortcut
Blender Addon : shortcut for HDRI global ligthning

{{ScriptInfo
|name= HDRI Lighting Shortcut
|tooltip= Easy setup for HDRI global lighting
|menu= Properties &rarr; World &rarr; HDRI-lighting-shortcut
|usage= Simply load a HDRI file to light your scene. See below for optional parameters
|version= 1.3.2
|blender= 2.78+
|category= Material
|author= [https://www.blendernetwork.org/nicolas-priniotakis-Nikos Priniotakis]
|license= DWTFYW V.2
|distribution= Extern
|note= 
|exe= HDRI-lighting-Shortcut-master.zip
|download=https://github.com/Nikos-Prinios/HDRI-lighting-Shortcut/archive/master.zip
|modules= os, bpy, getpass
|deps=
|data= 
|bugtracker= Send a mail to nikos (at) easy-logging (dot) net
|warning= 
|link=
|issues=
}}

== HDRI-lighting-shortcut ==

= DESCRIPTION =

"HDRI-lighting-shortcut" provides an easy way to setup a HDRI lighting to your scenes. Just load an image, make few optional adjustments and voilà.

= Installation =

# Download the latest version of "HDRI-lighting-shortcut" from the link above.
# Open Blender and go to File » User Preferences » Add-ons
# Click Install from File, navigate to the downloaded .zip (probably in your download folder), click Install from File.
# Activate the add-on by ticking the box (on the left side of the add-on's name).
# Click Save User Settings if you wish the add-on to be enabled by default.

Optional : Click on the expanding arrow to display the additional add-on information and preferences. In Preferences, pick your HDRI files folder. This way, you won't have to browse back to it in the future.

= Usage (basic) =

[[File:ui.png| left]]
In the Properties panel, click on the World tab and scroll down to HDRI-Lighting-Shortcut. Click on <b>"Load image"</b> and browse to a .HDR, .EXR (or .jpg and .png) file. The add-on will create a new world with a node setup. 

On the top of the panel, the name of your file appears inside the button. You can change this image at anytime by clicking on it. This will keep your adjustments (see below).

On the right side of the button, you can see an 'eye' and a 'X'.

#The eye : to show/hide the HDRI background
#The X : to remove the HDRI environnement and reset the parameters.

Some lighting settings appear under these buttons. They let you adjust some basic parameters :

#Ambient : The ambiant light strength
#Main : The main light (direct light) strength
#Orientation : The horizontal alignment of the HDRI image.

Note : <i>In the right panel of the 3D view, you can check 'World Background' (Display section) to display the environnement image in the viewport.</i>

= Usage (advanced) =

Checking the 'Adjustment' box gives you access to additional color adjustments:
<i>Saturation, Hue, a color correction wheel, exposure and blur.</i>

If most of these settings are self-explanatory, the two last ones deserve few words of explanations:

#Exposure : Adjust the exposure of the 3D scene without increasing the luminosity of the HDRI background image.
#Blur : Add a gaussian blur filter to your HDRI image.

= Release Notes =

1.3.2 – Fixed some bugs

1.0.0 – First public release (2015)
