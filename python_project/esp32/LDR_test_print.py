import utime
from machine import Pin, ADC

# ESP32 pin configuration
LIGHT_SENSOR_PIN1 = 36  # GPIO 36
LIGHT_SENSOR_PIN2 = 39  # GPIO 39
LED_PIN = Pin(5, Pin.OUT)

# Default sampling rate and position
sampling_rate = 3000  # milliseconds

# Read sensor values
def read_sensors():
    ldr1 = ADC(Pin(LIGHT_SENSOR_PIN1))
    ldr2 = ADC(Pin(LIGHT_SENSOR_PIN2))
    ldr1.atten(ADC.ATTN_11DB)
    ldr2.atten(ADC.ATTN_11DB)
    return ldr1.read(), ldr2.read()

# Read sensor values
def read_sensors_u16():
    #val = adc.read_u16()  # read a raw analog value in the range 0-65535
    ldr1 = ADC(Pin(LIGHT_SENSOR_PIN1))
    ldr2 = ADC(Pin(LIGHT_SENSOR_PIN2))
    return ldr1.read_u16(), ldr2.read_u16()

# Main function
def main():
    while True:
        LED_PIN.off()
        
        # Read sensors
        ldr1_value, ldr2_value = read_sensors()
        LED_PIN.on()
        print("Sensor values are: ", read_sensors_u16())
        # Delay based on the sampling rate
        utime.sleep_ms(sampling_rate)

# Run the main loop
main()