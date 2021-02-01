# join-modifiers-and-shapes
Join blender objects that contain modifiers and shape keys into a single object

## To install
* Download the JoinModifiersAndShapes.py and install through Blender Preferences -> Add-ons -> Install.
* Tick the check box next to "Object: Join Modifiers and Shapes" to enable it in the program. You're done!

## To use
Select stuff, then run the tool from Object Mode -> Tool Panel -> Join Modifiers & Shapes -> Crunchitize. The function will run, applying all modifiers and keeping & combining identically named shape keys in the final single mesh.

## NOTES
* This script will fail if a shape key affects a modifier in such a way that creates more or less vertices in the resulting shape.
* The main thing you have to watch out for is mirrored meshes with shape keys. Points merged along the meridian must stay on the meridian throughout all shape keys or the script will fail due to a mismatch in vertex numbers as different shape keys are applied. If you are getting errors, go through your shape keys and make sure that all meridian points on your mirrored meshes STAY on the meridian within all shape keys.
* This script takes exponentially more time the more objects + shape keys you wish to join together. It will not crash your Blender, it just takes a while

## Future plans
* Asymmetric shape key generation
* Progress bar

## Special thank yous
* To phosphenolic for helping me get going with Blender Python!
* To the Blender Team for making an awesome program free
