#!/usr/bin/env python
# -*- coding:utf-8 -*-

from skink.models import Project, Pipeline, PipelineItem
from skink.plugins import Plugin, Guard
import smtplib

no_host_message = "Please provide an 'smtp_host' configuration in the config.ini file, under the EmailPlugin section. This is required in order to define the SMTP server used to send the notifications."
no_user_message = "Please provide an 'smtp_user' configuration in the config.ini file, under the EmailPlugin section. This is required in order to define the user used to authenticate with the SMTP server."
no_pass_message = "Please provide an 'smtp_pass' configuration in the config.ini file, under the EmailPlugin section. This is required in order to define the password used to authenticate with the SMTP server."
no_sender_message = "Please provide an 'email_sender' configuration in the config.ini file, under the EmailPlugin section. This is required in order to define the e-mail used as sender in the notifications."
no_recipients_message = "Please provide an 'email_recipients' configuration in the config.ini file, under the EmailPlugin section. This is required in order to define the e-mails that will receive the notifications. This argument should be a semi-colon (;) separated list of e-mails."

class EmailPlugin (Plugin):
    section = "EmailPlugin" 
    config_keys = ("smtp_host", "smtp_user", "smtp_pass", "email_sender", "email_recipients")
    
    def __init__(self, configuration=None):
        super(EmailPlugin, self).__init__(configuration)

        self.enabled = self.configuration["enabled"]
        Guard.against_empty(self.enabled,'Please provide an "enabled" parameter, so I know if I should raise events.')
        
        if not self.enabled:
            return

        self.smtp_host = self.configuration.get('smtp_host',None)
        self.smtp_user = self.configuration.get('smtp_user',None)
        self.smtp_pass = self.configuration.get('smtp_pass',None)
        self.email_sender = self.configuration.get('email_sender',None)
        recipients = self.configuration.get('email_recipients', None) 
        self.email_recipients = recipients and recipients.split(';') or None

        Guard.against_empty(self.smtp_host, no_host_message)
        Guard.against_empty(self.smtp_user, no_user_message)
        Guard.against_empty(self.smtp_pass, no_pass_message)
        Guard.against_empty(self.email_sender, no_sender_message)
        Guard.against_empty(self.email_recipients, no_recipients_message)

    def __create_smtp_session__(self,host,user,password):
          session = smtplib.SMTP(host)
          session.login(user, password)
          return session

    def __send_email__(self, subject, msg):
        try:
            smtp_session = self.__create_smtp_session__(self.smtp_host,self.smtp_user,self.smtp_pass)
            smtp_session.set_debuglevel(1)
            recipients = ", ".join([recipient.strip() for recipient in self.email_recipients])
            body = "\r\n".join((
                                "From: %s" % self.email_sender,
                                "To: %s" % recipients,
                                "Subject: %s" % subject,
                                "",
                                msg
                              ))

            smtp_result = smtp_session.sendmail(self.email_sender, recipients, body)

            if smtp_result:
                errstr = ""
                for recip in smtp_result.keys():
                    errstr = """Could not deliver mail to: %s

                    Server said: %s
                    %s
                    
                    %s""" % (recip, smtp_result[recip][0], smtp_result[recip][1], errstr)
                raise smtplib.SMTPException, errstr
        except Exception, e:
            print 'disabling plugin %s' %e
            self.enabled = False

    def on_project_created(self, project):
        print(" ==> on_project_created")

    def on_project_updated(self, project):
        print(" ==> on_project_updated")

    def on_project_deleted(self, project):
        print(" ==> on_project_deleted")

    def on_pipeline_created(self, pipeline):
        print(" ==> on_pipeline_created")

    def on_pipeline_updated(self, pipeline):
        print(" ==> on_pipeline_updated")

    def on_pipeline_deleted(self, pipeline):
        print(" ==> on_pipeline_deleted")

    def on_before_build(self, project):
        print(" ==> on_before_build raised")

    def on_build_successful(self, project, build):
        print(" ==> on_build_successful")
        self.__send_email__("[Skink] PROJECT %s was built successfully" % project.name, 
                            "project [%s], build [%s] successfully :) " %(project.name,build.number))

    def on_build_failed(self, project, build):
        print(" ==> on_build_failed")
        self.__send_email__("[Skink] PROJECT %s failed the build" % project.name, 
                            "project [%s], build [%s] failed :(" %(project.name,build.number))
