import paho.mqtt.client as mqtt

class IoT_Controller:
    client = None
    #TODO: support for collections of conditions leading to single outputs
    rules = [
                {
                        "condition":{"topic":"house/temp", "comparison":">", "value":30},
                        "action":{"message":"It's too hot,turn on the AC", "topic":"room/AC","value":"On"}
                },
                {
                        "condition":{"topic":"house/temp", "comparison":"<", "value":20},
                        "action":{"message":"It's too cold,turn on the heat", "topic":"room/heat","value":"On"}
                }
        ]


    def configure():
        IoT_Controller.client = mqtt.Client()
        #pass the reference to the callback function to handle incoming messages
        IoT_Controller.client.on_message = IoT_Controller.on_message
        #must connect to the MQTT message broker at "localhost" on port 1883
        IoT_Controller.client.connect("localhost",1883)
        IoT_Controller.client.subscribe("#")

    def on_message(client, userdata, message):
        #this is where we handle the messages
        #using try..except (exception handling)
        try:
            value = float(message.payload.decode("utf-8"))
        except ValueError:
            print("String")
            value = message.payload.decode("utf-8")
        topic = message.topic
        #the only action is the printout
        print(topic, value)

        #based on the value(s) on the topic(s) received trigger an action

        #loop through the rules
#                {
#                        "condition":{"topic":"house/temp", "comparison":">", "value":30},
#                        "action":{"message":"It's too hot,turn on the AC", "topic":"room/AC","value","On"}
#                },

        for rule in IoT_Controller.rules:
            condition = rule["condition"]
            action = rule["action"]
            if topic == condition["topic"] and IoT_Controller.condition_met(value,condition["comparison"],condition["value"]):
                #action
                print(action["message"])
                IoT_Controller.client.publish(action["topic"],action["value"])

    def condition_met(value,comp_operator,comp_value):
        if comp_operator == ">":
            return value > comp_value
        if comp_operator == ">=":
            return value > comp_value
        if comp_operator == "<":
            return value > comp_value
        if comp_operator == "<=":
            return value > comp_value
        if comp_operator == "==":
            return value > comp_value

    def run():
        IoT_Controller.client.loop_forever()

def main():
    IoT_Controller.configure()
    IoT_Controller.run()

if __name__== "__main__":
    main()
