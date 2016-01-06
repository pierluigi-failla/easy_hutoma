# -*- coding: utf-8 -*-

import json
import logging
from requests import Session

# Refer to Hutoma API: [ base url: /api/v1 , api version: 0.5.0 ]


class HutomaException(Exception):
    """ A class for Hutoma Exceptions
    """

    def __init__(self, error_code=None, error_type=None, error_details=None, message=None, sender=None):
        super(HutomaException, self).__init__()
        self.message = 'Error Code: {0} Error Type: {1} Error Details: {2} Message: {3} Sender: {4}'.format(error_code,
                                                                                                            error_type,
                                                                                                            error_details,
                                                                                                            message,
                                                                                                            sender)
        self.error_code = error_code
        self.error_type = error_type
        self.error_details = error_details
        self.sender = sender

    def __str__(self):
        return self.message


class EasyHutoma(object):
    """ A class to interact with Hutoma API
    """

    AI_STATUSES = [
        'start',  # load the AI in memory
        'stop',  # shut it down AI
        'reload',  # force the AI to reload the underlying neural network
        'compile',  # ensure there are no errors in the files you provided
    ]

    def __init__(self, user_key, base_url='https://api-2445581341197.apicast.io:443/api/v1/'):
        """
        Create a EasyHutoma object
        :param user_key: is your api key
        :param base_url: is the main api url
        """
        self._user_key = user_key
        self._base_url = base_url
        self._api_calls = 0  # count how many api calls for this session

    def _request(self, method, end_point_url, params={}, files=None):
        """
        Run requests for this sessions
        :param method: can be one in [GET, POST, DELETE, PUT]
        :param end_point_url: the end point name
        :param params: (optional) additional parameters for the url
        :param files: (optional) files to be uploaded
        :return: a response (a dictionary) or raise an HutomaException
        """
        session = Session()
        session.headers['user_key'] = self._user_key
        url = self._base_url + end_point_url.format(**params)
        method = method.upper()

        logging.debug('API call {0}: {1}'.format(method, end_point_url.format(**params)))
        response = session.request(method=method,
                                   url=url,
                                   files=files,
                                   timeout=None)

        logging.debug('  Response: {0}'.format(response.__dict__))

        self._api_calls += 1

        if response.status_code >= 400:
            raise HutomaException(
                    error_code=response.status_code,
                    error_details=response.raw,
                    message=response._content,
                    sender='_request {0} {1}'.format(method, end_point_url.format(**params))
            )

        response = json.loads(response.content)

        logging.debug('  Response keys: {0}'.format(response.keys()))
        logging.debug('  Response: {0}'.format(response))

        if 'code' in response:
            response = {'status': response}
        if response['status']['code'] == 200:
            # del response['status']
            return response

        raise HutomaException(
                error_code=response['status']['code'],
                error_type=response['status']['errorType'],
                error_details=response['status']['errorDetails'],
                sender='_request {0} {1}'.format(method, end_point_url.format(**params))
        )

    def _check_aiid(self, aiid):
        """ Raise an exception if the aiid is not valid
        """
        if not aiid or not isinstance(aiid, basestring):
            raise HutomaException(
                    message='Aiid: {0} is not a valid aiid'.format(aiid),
                    sender='_check_aiid'
            )

    def _check_status(self, status):
        """ Raise an exception if the status is not valid
        """
        if not status or status.lower() not in self.AI_STATUSES:
            raise HutomaException(
                    message='Status: {0} is not a valid status'.format(status),
                    sender='_check_status'
            )

    def api_calls_count(self):
        """ Return the number of APIs call for this session
        """
        return self._api_calls

    def list_ai(self):
        """
        Enumerate all active AI
        :return: a list of available AIs
        """
        try:
            response = self._request(
                    'GET',
                    'ai/'
            )
        except HutomaException as e:
            logging.warn('list_ai: ' + e.message)
            raise
        return response['AIs']

    def create_ai(self):
        """
        Create a new AI
        :return: a list of available AIs
        """
        try:
            response = self._request(
                    'POST',
                    'ai/'
            )
        except HutomaException as e:
            logging.warn('create_ai: ' + e.message)
            raise
        return response['AIs']

    def delete_ai(self, aiid):
        """
        Delete an AI and every file associated to it
        :param aiid: the AI id
        :return: a list of available AIs
        """
        self._check_aiid(aiid)
        try:
            response = self._request(
                    'DELETE',
                    'ai/{aiid:s}/',
                    params={'aiid': aiid}
            )
        except HutomaException as e:
            logging.warn('delete_ai: ' + e.message)
            raise
        return response['AIs']

    def current_status(self, aiid):
        """
        Returns an object summarizing the overall AI runtime status. If the AI is in training, it will also return
        usefull information about that.
        :param aiid: the AI id
        :return: ({
                    trainingStatus (integer, optional): A numerical value indicating the status of the training
                                                        process 0 - request queued 1 - training in process 2 -
                                                        training completed 3 - stopping 4 - stopped 5 - max training
                                                        time reached
                    trainingStatusDetails (string, optional): Details about the trainingStatus code
                    runtimeStatus (integer, optional): A numerical value indicating the runtime status of your AI.
                                                       0 means the AI is not running. 1 means the AI is running and
                                                       can be queried.
                    runtimeStatusDetails (string, optional): Details about the runtimeStatus code
                    score (integer, optional): The score field provides a quantitative metric to help you assess how
                                               well the network is learning your sample data. At each learning
                                               iteration, the API will compute a training error function that tells
                                               you how far your bot is from completely learning the training data.
                                               The training process will automatically stop once this function
                                               reaches 0 (or you reached your allocated traning time).
                    sample (string, optional): An example of how the neural network would answer to a question if
                                               queried at this moment in time durin the training. If the answer do
                                               not make sense let the network train for longer
                },
                {
                    runtimeStatusDetails (string, optional): [not in the documentation]
                    runtimeStatus (integer, optional): [not in the documentation]
                    compileError (string, optional): [not in the documentation]
                })
        """
        self._check_aiid(aiid)
        try:
            response = self._request(
                    'GET',
                    'ai/{aiid:s}/',
                    params={'aiid': aiid}
            )
        except HutomaException as e:
            logging.warn('current_status: ' + e.message)
            raise
        return response['neuralnetwork'], response['aiml']

    def change_status(self, aiid, status):
        """
        Loads/Unloads an AI in memory or verifies that the AI compiles correctly. Use this api to load an AI in
        memory to reduce the time needed to get an answer back the first time it is pinged. It can be also used to
        reload the undelying neural network if changes have happened (for example, a more precise model has been
        produced by the training). Moreover, if you code specific AI behaviours via AIML2.0 you can compile the
        supplied files to verify they are correct.
        :param aiid: the AI id
        :param status: on of the AI_STATUSES
        :return: ({
                    trainingStatus (integer, optional): A numerical value indicating the status of the training
                                                        process 0 - request queued 1 - training in process 2 -
                                                        training completed 3 - stopping 4 - stopped 5 - max training
                                                        time reached
                    trainingStatusDetails (string, optional): Details about the trainingStatus code
                    runtimeStatus (integer, optional): A numerical value indicating the runtime status of your AI.
                                                       0 means the AI is not running. 1 means the AI is running and
                                                       can be queried. ,
                    runtimeStatusDetails (string, optional): Details about the runtimeStatus code ,
                    score (integer, optional): The score field provides a quantitative metric to help you assess how
                                               well the network is learning your sample data. At each learning
                                               iteration, the API will compute a training error function that tells
                                               you how far your bot is from completely learning the training data.
                                               The training process will automatically stop once this function
                                               reaches 0 (or you reached your allocated traning time).
                    sample (string, optional): An example of how the neural network would answer to a question if
                                               queried at this moment in time durin the training. If the answer do
                                               not make sense let the network train for longer
                },
                {
                    runtimeStatusDetails (string, optional): [not in the documentation]
                    runtimeStatus (integer, optional): [not in the documentation]
                    compileError (string, optional): [not in the documentation]
                })
        """
        self._check_aiid(aiid)
        self._check_status(status)
        try:
            response = self._request(
                    'GET',
                    'ai/{aiid:s}?action={status:s}',
                    params={'aiid': aiid, 'status': status}
            )
        except HutomaException as e:
            logging.warn('change_status: ' + e.message)
            raise
        return response['neuralnetwork'], response['aiml']

    def files_in_folder(self, aiid, folder):
        """
        List file in a folder
        :param aiid: the AI id
        :param folder: folder name
        :return: a list of filenames in the folder
        """
        self._check_aiid(aiid)
        if not folder:
            raise HutomaException('folder: {0} is not a valid folder name'.format(folder))
        try:
            response = self._request(
                    'GET',
                    'ai/{aiid:s}/{folder:s}/',
                    params={'aiid': aiid, 'folder': folder}
            )
        except HutomaException as e:
            logging.warn('files_in_folder: ' + e.message)
            raise
        return response['files']

    def upload_file_in_folder(self, aiid, folder, file_path):
        """
        Upload file to a folder
        :param aiid: the AI id
        :param folder: folder name
        :param file_path: path to the file to upload
        :return: True or HutomaException
        """
        self._check_aiid(aiid)
        if not folder:
            raise HutomaException('folder: {0} is not a valid folder'.format(folder))
        files = {'file': open(file_path, 'rb')}
        try:
            response = self._request(
                    'POST',
                    'ai/{aiid:s}/{folder:s}/',
                    params={'aiid': aiid, 'folder': folder},
                    files=files
            )
        except HutomaException as e:
            logging.warn('upload_file_in_folder: ' + e.message)
            raise
        return True

    def delete_folder(self, aiid, folder):
        """
        Delete the content of a folder
        :param aiid: the AI id
        :param folder: folder name
        :return: True or HutomaException
        """
        self._check_aiid(aiid)
        if not folder:
            raise HutomaException('folder: {0} is not a valid folder'.format(folder))
        try:
            response = self._request(
                    'DELETE',
                    'ai/{aiid:s}/{folder:s}/',
                    params={'aiid': aiid, 'folder': folder}
            )
        except HutomaException as e:
            logging.warn('delete_folder: ' + e.message)
            raise
        return True

    def chat(self, aiid, uid, q, debug=False):
        """
        Text with an AI
        :param aiid: the AI id
        :param uid: (integer) a unique identifier associated to the user talking to the AI
        :param q: a sentent or query for the AI
        :param debug: If set to True, the response returned by the AI will return useful debug information
        :return: a string containing the AI answer
        """
        self._check_aiid(aiid)
        try:
            response = self._request(
                    'GET',
                    'ai/{aiid:s}/chat?debug={debug:s}&q={q:s}&uid={uid:d}',
                    params={'aiid': aiid, 'debug': 'true' if debug else 'false', 'q': q, 'uid': uid}
            )
        except HutomaException as e:
            logging.warn('chat: ' + e.message)
            raise
        return response['output']

    def speak(self, aiid, uid, utterance_file_path, voice=0, debug=False):
        # TODO(pierluigi) this function needs to be tested
        """
        Speak with an AI
        :param aiid: the AI id
        :param uid: (integer) a unique identifier associated to the user talking to the AI
        :param utterance_file_path: A binary stream containing an utterance. The utterance can be either a
                                    wave/mp3 file or a captured live from the microphone.
        :param voice: Set voice =0 to hear a response with a female voice. Set voice=1 to use a male voice.
        :param debug: If set to True, the response returned by the AI will return useful debug information
        :return: {
                    input (string, optional): the input string
                    confidence (number, optional): a value indicating the confidence level for the recognized utterance
                    output (string, optional): the response to the input string. If the debug field is set,
                                               additional information will be provided
                    tts (string, optional): a binary stream containing the spoken version of the output field
                }
        """
        self._check_aiid(aiid)
        if voice > 0:
            voice = 1  # male voice
        files = {'file': open(utterance_file_path, 'rb')}
        try:
            response = self._request(
                    'GET',
                    'ai/{aiid:s}/speak?debug={debug:s}&voice={voice:d}&uid={uid:d}',
                    params={'aiid': aiid, 'debug': 'true' if debug else 'false', 'voice': voice, 'uid': uid},
                    files=files
            )
        except HutomaException as e:
            logging.warn('speak: ' + e.message)
            raise
        del response['code']
        del response['message']
        return response

    def training_start(self, aiid):
        """
        Start training
        :param aiid: the AI id
        :return: ({
                    trainingStatus (integer, optional): A numerical value indicating the status of the training
                                                        process 0 - request queued 1 - training in process 2 -
                                                        training completed 3 - stopping 4 - stopped 5 - max training
                                                        time reached
                    trainingStatusDetails (string, optional): Details about the trainingStatus code
                    runtimeStatus (integer, optional): A numerical value indicating the runtime status of your AI.
                                                       0 means the AI is not running. 1 means the AI is running and
                                                       can be queried. ,
                    runtimeStatusDetails (string, optional): Details about the runtimeStatus code ,
                    score (integer, optional): The score field provides a quantitative metric to help you assess how
                                               well the network is learning your sample data. At each learning
                                               iteration, the API will compute a training error function that tells
                                               you how far your bot is from completely learning the training data.
                                               The training process will automatically stop once this function
                                               reaches 0 (or you reached your allocated traning time).
                    sample (string, optional): An example of how the neural network would answer to a question if
                                               queried at this moment in time durin the training. If the answer do
                                               not make sense let the network train for longer
                },
                {
                    runtimeStatusDetails (string, optional): [not in the documentation]
                    runtimeStatus (integer, optional): [not in the documentation]
                    compileError (string, optional): [not in the documentation]
                })
        """
        self._check_aiid(aiid)
        try:
            response = self._request(
                    'PUT',
                    'ai/{aiid:s}/training?action=start',
                    params={'aiid': aiid}
            )
        except HutomaException as e:
            logging.warn('training_start: ' + e.message)
            raise
        return response['neuralnetwork'], response['aiml']

    def training_stop(self, aiid):
        """
        Stop training
        :param aiid: the AI id
        :return: ({
                    trainingStatus (integer, optional): A numerical value indicating the status of the training
                                                        process 0 - request queued 1 - training in process 2 -
                                                        training completed 3 - stopping 4 - stopped 5 - max training
                                                        time reached
                    trainingStatusDetails (string, optional): Details about the trainingStatus code
                    runtimeStatus (integer, optional): A numerical value indicating the runtime status of your AI.
                                                       0 means the AI is not running. 1 means the AI is running and
                                                       can be queried. ,
                    runtimeStatusDetails (string, optional): Details about the runtimeStatus code ,
                    score (integer, optional): The score field provides a quantitative metric to help you assess how
                                               well the network is learning your sample data. At each learning
                                               iteration, the API will compute a training error function that tells
                                               you how far your bot is from completely learning the training data.
                                               The training process will automatically stop once this function
                                               reaches 0 (or you reached your allocated traning time).
                    sample (string, optional): An example of how the neural network would answer to a question if
                                               queried at this moment in time durin the training. If the answer do
                                               not make sense let the network train for longer
                },
                {
                    runtimeStatusDetails (string, optional): [not in the documentation]
                    runtimeStatus (integer, optional): [not in the documentation]
                    compileError (string, optional): [not in the documentation]
                })
        """
        self._check_aiid(aiid)
        try:
            response = self._request(
                    'PUT',
                    'ai/{aiid:s}/training?action=stop',
                    params={'aiid': aiid}
            )
        except HutomaException as e:
            logging.warn('training_stop: ' + e.message)
            raise
        return response['neuralnetwork'], response['aiml']

    def training_delete(self, aiid):
        """
        Delete a training
        :param aiid: the AI id
        :return: True or HutomaException
        """
        self._check_aiid(aiid)
        try:
            response = self._request(
                    'DELETE',
                    'ai/{aiid:s}/training',
                    params={'aiid': aiid}
            )
        except HutomaException as e:
            logging.warn('training_delete: ' + e.message)
            raise
        return True

    def training_upload_source(self, aiid, file_path):
        """
        Upload the source.txt file
        :param aiid: the AI id
        :param file_path: path to the target.txt
        :return: True or HutomaException
        """
        self._check_aiid(aiid)
        if 'source.txt' not in file_path:
            raise HutomaException('source filename: {0} should be source.txt'.format(file_path))
        files = {'file': open(file_path, 'rb')}
        try:
            response = self._request(
                    'POST',
                    'ai/{aiid:s}/training',
                    params={'aiid': aiid},
                    files=files
            )
        except HutomaException as e:
            logging.warn('training_upload_source: ' + e.message)
            raise
        return True

    def training_upload_target(self, aiid, file_path):
        """
        Upload the target.txt file
        :param aiid: the AI id
        :param file_path: path to the source.txt
        :return: True or HutomaException
        """
        self._check_aiid(aiid)
        if 'target.txt' not in file_path:
            raise HutomaException('source filename: {0} should be target.txt'.format(file_path))
        files = {'file': open(file_path, 'rb')}
        try:
            response = self._request(
                    'POST',
                    'ai/{aiid:s}/training',
                    params={'aiid': aiid},
                    files=files
            )
        except HutomaException as e:
            logging.warn('training_upload_target: ' + e.message)
            raise
        return True

    def training_upload_files(self, aiid, source_file_path, target_file_path):
        """
        Upload the source and target files
        :param aiid: the AI id
        :param source_file_path: path to the source.txt
        :param target_file_path: path to the target.txt
        :return: True if both uploads were fine or HutomaException
        """
        self.training_upload_source(aiid, source_file_path)
        self.training_upload_target(aiid, target_file_path)
        return True
