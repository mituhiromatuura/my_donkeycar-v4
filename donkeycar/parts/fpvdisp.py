import os
import time
import numpy as np
import cv2
import concurrent.futures
import queue
import RPi.GPIO as GPIO

class FPVDisp:
	def __init__(self, cfg):

		self.cfg = cfg
		self.on = True
		self.deg = 0
		self.lap = 0

	def run(self,
		num_records,
		image,
		cycle_time,
		volt_a,
		volt_b,
		mode,
		angle,
		throttle,
		rpm,
		lap,
		lidar,
		esc_on,
		disp_on,
		recording,
		ch1,
		ch2,
		ch3,
		ch4,
		ch5,
		ch6,
		gyr_z,
		):

		kmph = round(rpm * self.cfg.KMPH, 2)
		if self.on:

			if disp_on:

				wwidth = self.cfg.IMAGE_W
				wheight = self.cfg.IMAGE_H
				img = image.copy()

				if recording:
					color = (255,0,0) #red
				elif not esc_on:
					color = (255,255,0) #yellow
				else:
					color = (0,255,0) #green

				x0=int(round(wwidth/2))
				y0=int(round(wheight))
				x1=int(round(wwidth/2 + wwidth/2*angle * (1 if self.cfg.SBUS_CH1_MIN < self.cfg.SBUS_CH1_MAX else -1)))
				y1=int(round(wheight + wheight*throttle * (1 if self.cfg.SBUS_CH2_MIN < self.cfg.SBUS_CH2_MAX else -1)))
				cv2.line(img,(x0 ,y0),(x1,y1),color,2)

				def printText(img, str, xy, textColor=(0,255,0)):
					textFontFace = cv2.FONT_HERSHEY_SIMPLEX
					textFontScale = 0.4
					#textColor = (0,255,0)
					textThickness = 1
					cv2.putText(img, str, xy, textFontFace,textFontScale,textColor,textThickness)

				printText(img, str(ch1), (wwidth-8*9,wheight-11))
				printText(img, str(ch2), (wwidth-8*4,wheight-11))

				printText(img, str(num_records), (wwidth-8*5,wheight-21))
				printText(img, mode, (0,9))

				if esc_on:
					printText(img, 'ESC ON', (wwidth-8*6,9), (255,0,0))
				else:
					printText(img, 'ESC OFF', (wwidth-8*7,9))

				if recording:
					printText(img, 'REC ON', (wwidth-8*6,19), (255,0,0))
				else:
					printText(img, 'REC OFF', (wwidth-8*7,19))

				printText(img, str(ch3), (0,19))
				printText(img, str(ch4), (0,29))
				printText(img, str(ch5), (0,39))
				printText(img, str(ch6), (0,49))

				if self.cfg.HAVE_LIDAR:
					printText(img, str(lidar), (0,59))

				if self.cfg.HAVE_AHRS:
					if not esc_on:
						self.deg = 0
					else:
						self.deg += cycle_time * gyr_z
						self.lap = int(self.deg / 1000 // 360)
					printText(img, str(self.lap), (0,wheight-21))

				if self.cfg.HAVE_INA226:
					printText(img, "{:.2f}".format(volt_b), (0,wheight-11))
					printText(img, "{:.2f}".format(volt_a), (0,wheight-1))

				if self.cfg.HAVE_REVCOUNT:
					printText(img, str(rpm), (wwidth-8*9,wheight-1))
					printText(img, "{:.1f}".format(kmph), (8*5,wheight-1))

				printText(img, "{:.1f}".format(cycle_time), (wwidth-8*7//2,wheight-1))

				cv2.namedWindow('DonkeyCamera', cv2.WINDOW_NORMAL)
				cv2.resizeWindow("DonkeyCamera", wwidth, wheight)
				cv2.imshow('DonkeyCamera', img[:,:,::-1])
				wk = cv2.waitKey(1) & 0xff
				if wk == 99 or wk == 27: # ctrl-c or esc
					cv2.destroyAllWindows()
					self.on = False

		return kmph

	def shutdown(self):
		self.on = False
		print("FPVDisp shutdown")
