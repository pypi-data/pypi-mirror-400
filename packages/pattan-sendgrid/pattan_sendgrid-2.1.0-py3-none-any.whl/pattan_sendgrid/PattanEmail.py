from sendgrid import SendGridAPIClient
from .exceptions import MailSendFailure, MalformedConfiguration, BadSenderObject
from pattan_sendgrid.models import Config

class PattanEmail:
    """
    Useful SendGrid API abstraction for sending emails.
    It includes a command line interface to construct the configuration file by querying the SendGrid API directly.
    """
    def __init__(self, config_json=None ):
        if not config_json:
            raise MalformedConfiguration
        try:
            # pydantic validator makes sure each property is defined and has a default value set
            self.config = Config.model_validate_json(config_json)
        except Exception as e:
            raise MalformedConfiguration

        self.api_key = self.config.api_key
        self.ip_pool = self.config.ip_pools
        self.unsubscribe_groups = self.config.unsubscribe_groups
        self.senders = self.config.senders
        self.templates = self.config.email_templates
        self.sg = SendGridAPIClient(api_key=self.api_key)



    def send_template_email(self, to_addr, dynamic_template_data=None, sender='DEFAULT', 
                            email_template="DEFAULT", asm_group="DEFAULT", ip_pool="DEFAULT"):
        """
        Send the same email to one or more recipients.
        :param to_addr: email address dict or list of address dicts e.g. [{'name':'bob', 'email':'bob@example.com'}],
        :param dynamic_template_data: dict that defines all the variables used in the selected email_template
        :param email_template: string Name of the template you want to use e.g. "PaTTAN Standard Template"
        :param sender: string Name of the sender email address, e.g. "no-reply@PaTTAN"; or email address dict
        :param asm_group: string Name of the asm group (a.k.a. unsubscribe group)  e.g. "SendGrid Tech Test Group"
        :param ip_pool: string Name of the ip_pool e.g. "Pattan_Transactional"
        :return: SendGrid client response or throws an exception
        """

        from_email = self.get_from_email_from_sender(sender)

        # the to_addr can be a list of just a string or an email address.
        if isinstance(to_addr, str):
            to_addr = [{'name': to_addr, 'email': to_addr}]

        personalizations = [{
            'to': to_addr,
            'dynamic_template_data': dynamic_template_data,
        }]

        asm = {
            'group_id': self.unsubscribe_groups[asm_group].id,
            'groups_to_display': [
                self.unsubscribe_groups[asm_group].id
            ]
        }

        template_id = self.templates[email_template].id

        message = {
            "from": from_email,
            "personalizations": personalizations,
            "template_id": template_id,
            "asm": asm,
            "ip_pool_name": self.ip_pool[ip_pool].name,
        }

        try:
            sg_response = self.sg.client.mail.send.post(request_body=message)
        except Exception as e:
            raise MailSendFailure
        return sg_response

    def send_personalized_template_email(self, personalization_list, template_id, sender='DEFAULT',
                                         asm_group="DEFAULT", ip_pool="DEFAULT"):
        """
        This function should be used when the email is customized for each recipient.
        :param personalization_list: contains a sender tuple and all the parameters in the sendgrid template.
        :return:
        """
        from_email = self.get_from_email_from_sender(sender)

        asm = {
            'group_id': self.unsubscribe_groups[asm_group].id,
            'groups_to_display': [
                self.unsubscribe_groups[asm_group].id
            ]
        }

        message = {
            'asm': asm,
            'from': from_email,
            'ip_pool_name': self.ip_pool[ip_pool].name,
            'template_id': template_id,
            'personalizations': personalization_list
        }

        try:
            sg_response = self.sg.client.mail.send.post(request_body=message)
        except Exception as e:
            raise MailSendFailure
        return sg_response


    def get_from_email_from_sender(self, sender):
        if isinstance(sender, str):
            if sender not in self.senders.keys():
                raise MalformedConfiguration('Assigned sender is not defined in your configuration')

            sender = self.senders[sender]
            from_email = {'email': sender.from_address.email}
            if sender.nickname:
                from_email['name'] = sender.nickname
            
            return from_email
        
        else:
            if 'email' in sender:
                from_email = {'email': sender['email']}
                if 'name' in sender:
                    from_email['name'] = sender['name']
                
                return from_email
            
            else:
                raise BadSenderObject
