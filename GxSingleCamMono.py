# version:1.1.2312.9221
import gxipy as gx
from PIL import Image
from ctypes import *
from gxipy.gxidef import *
import numpy
from gxipy.ImageProc import Utility

def get_best_valid_bits(pixel_format):
    valid_bits = DxValidBit.BIT0_7
    if pixel_format in (GxPixelFormatEntry.MONO8, GxPixelFormatEntry.BAYER_GR8, GxPixelFormatEntry.BAYER_RG8, GxPixelFormatEntry.BAYER_GB8, GxPixelFormatEntry.BAYER_BG8
                        , GxPixelFormatEntry.RGB8, GxPixelFormatEntry.BGR8, GxPixelFormatEntry.R8, GxPixelFormatEntry.B8, GxPixelFormatEntry.G8):
        valid_bits = DxValidBit.BIT0_7
    elif pixel_format in (GxPixelFormatEntry.MONO10, GxPixelFormatEntry.MONO10_PACKED, GxPixelFormatEntry.BAYER_GR10,
                          GxPixelFormatEntry.BAYER_RG10, GxPixelFormatEntry.BAYER_GB10, GxPixelFormatEntry.BAYER_BG10):
        valid_bits = DxValidBit.BIT2_9
    elif pixel_format in (GxPixelFormatEntry.MONO12, GxPixelFormatEntry.MONO12_PACKED, GxPixelFormatEntry.BAYER_GR12,
                          GxPixelFormatEntry.BAYER_RG12, GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_BG12):
        valid_bits = DxValidBit.BIT4_11
    elif pixel_format in (GxPixelFormatEntry.MONO14):
        valid_bits = DxValidBit.BIT6_13
    elif pixel_format in (GxPixelFormatEntry.MONO16):
        valid_bits = DxValidBit.BIT8_15
    return valid_bits

def convert_to_special_pixel_format(raw_image, pixel_format):
    image_convert.set_dest_format(pixel_format)
    valid_bits = get_best_valid_bits(raw_image.get_pixel_format())
    image_convert.set_valid_bits(valid_bits)

    # create out put image buffer
    buffer_out_size = image_convert.get_buffer_size_for_conversion(raw_image)
    output_image_array = (c_ubyte * buffer_out_size)()
    output_image = addressof(output_image_array)

    #convert to pixel_format
    image_convert.convert(raw_image, output_image, buffer_out_size, False)
    if output_image is None:
        print('Pixel format conversion failed')
        return

    return output_image_array, buffer_out_size

def get_pixel(image):
    width, height = image.size
    # Use a list comprehension to populate a list with RGB values of each pixel.
    pixel_values = ([image.getpixel((x, y)) for y in range(height) for x in range(width)])
    # Print the RGB value of the first pixel.
    #print("Value of the first pixel:", pixel_values[0])
    # Loop through the list and print RGB values of each pixel.
    # for idx, value in enumerate(pixel_values):
    #     print(f"Value of pixel {idx}: {value}")
    return width, height, pixel_values

'''
# Extracting RGB Values from Images
def get_rgb_value(image):

    image = image.convert('RGB')

    # Retrieve the width and height of the image.
    width, height = image.size

    # Use a list comprehension to populate a list with RGB values of each pixel.
    rgb_values = [image.getpixel((x, y)) for y in range(height) for x in range(width)]

    # Print the RGB value of the first pixel.
    #print("RGB value of the first pixel:", rgb_values[0])

    # Loop through the list and print RGB values of each pixel.
    # write in file
    file_path = r"C:\Program Files\Daheng Imaging\GalaxySDK\Development\Doc\rgb.txt"
    with open(file_path, "w") as f:
        for idx, value in enumerate(rgb_values):
            print(f"RGB value of pixel {idx}: {value}")
            f.write(f"RGB value of pixel {idx}: {value}\n")
'''   
def main():
    # print the demo information
    print("")
    print("-------------------------------------------------------------")
    print("Sample to show how to acquire mono image continuously and show acquired image.")
    print("-------------------------------------------------------------")
    print("")
    print("Initializing......")
    print("")

    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_all_device_list()
    if dev_num is 0:
        print("Number of enumerated devices is 0")
        return

    # open the first device
    cam = device_manager.open_device_by_index(1)
    remote_device_feature = cam.get_remote_device_feature_control()

    # get image convert obj
    global image_convert
    image_convert = device_manager.create_image_format_convert()

    # exit when the camera is a color camera
    pixel_format_value, pixel_format_str = remote_device_feature.get_enum_feature("PixelFormat").get()
    if Utility.is_gray(pixel_format_value) is False:
        print("This sample does not support color camera.")
        cam.close_device()
        return

    # set continuous acquisition
    trigger_mode_feature = remote_device_feature.get_enum_feature("TriggerMode")
    trigger_mode_feature.set("Off")

    # start data acquisition
    cam.stream_on()

    # acquire image: num is the image number
    num = 1
    for i in range(num):
        # get raw image
        raw_image = cam.data_stream[0].get_image()
        if raw_image is None:
            print("Getting image failed.")
            continue
        if raw_image.get_pixel_format() not in (GxPixelFormatEntry.MONO8, GxPixelFormatEntry.R8, GxPixelFormatEntry.B8, GxPixelFormatEntry.G8):
            mono_image_array, mono_image_buffer_length = convert_to_special_pixel_format(raw_image,
                                                                                         GxPixelFormatEntry.MONO8)
            if mono_image_array is None:
                return
            # create numpy array with data from rgb image
            numpy_image = numpy.frombuffer(mono_image_array, dtype=numpy.ubyte, count=mono_image_buffer_length). \
                reshape(raw_image.frame_data.height, raw_image.frame_data.width)
        else:
            numpy_image = raw_image.get_numpy_array()

        if numpy_image is None:
            continue

        # show acquired image
        #print(numpy_image)
        img = Image.fromarray(numpy_image, 'L')
        #img.show()

        print(img.size)

        # print pixel values
        width, height, pixel_array = get_pixel(img)
        a=[]
        b=[]
        c=[]
        d=[]
        for i in range(height):
            for j in range(width):
                if (i%2) == 0 and (j%2) == 0:
                    a.append(pixel_array[j])
                elif (i%2) == 0 and (j%2) != 0:
                    b.append(pixel_array[j])
                elif (i%2) != 0 and (j%2) == 0:
                    c.append(pixel_array[j])
                elif (i%2) != 0 and (j%2) != 0:
                    d.append(pixel_array[j])
                else:
                    print('Pixel allocations not applicable')
        print("Angle 90° size %s" % len(a))
        print("Angle 45° size %s" % len(b))
        print("Angle 135° size %s" % len(c))
        print("Angle 0° size %s" % len(d))
        #for i in range(len(a)):
            #print('pixel %s value is %s' % (i, a[i]), end = ' ')

        # print height, width, and frame ID of the acquisition image
        #print("Frame ID: %d   Height: %d   Width: %d  Pixel Format: %d"
              #% (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width(), raw_image.get_pixel_format()))

    # stop data acquisition
    cam.stream_off()

    # close device
    cam.close_device()

if __name__ == "__main__":
    main()
