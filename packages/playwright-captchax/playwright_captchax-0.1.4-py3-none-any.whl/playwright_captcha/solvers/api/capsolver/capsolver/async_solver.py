#!/usr/bin/env python3

import asyncio
import time
from base64 import b64encode

import httpx

from .async_api import AsyncApiClient
from .exceptions.solver import ValidationException, NetworkException, TimeoutException, ApiException, \
    SolverExceptions


class AsyncCapSolver:
    def __init__(self,
                 apiKey,
                 appId=None,
                 defaultTimeout=120,
                 recaptchaTimeout=600,
                 pollingInterval=3,
                 server='https://api.capsolver.com',
                 verify_ssl=True):

        self.API_KEY = apiKey
        self.app_id = appId
        self.default_timeout = defaultTimeout
        self.recaptcha_timeout = recaptchaTimeout
        self.polling_interval = pollingInterval
        self.verify_ssl = verify_ssl
        self.api_client = AsyncApiClient(base_url=server, verify_ssl=verify_ssl)
        self.exceptions = SolverExceptions

    async def recaptcha(self, sitekey, url, version='v2', enterprise=False, **kwargs):
        """Wrapper for solving recaptcha (v2, v3).

        Parameters
        _______________
        sitekey : str
            Value of sitekey parameter you found on page.
        url : str
            Full URL of the page where you see the reCAPTCHA.
        version : str, optional
            v3 — defines that you're sending a reCAPTCHA V3. Default: v2.
        enterprise : bool, optional
            True - defines that you're sending reCAPTCHA Enterprise. Default: False.
        invisible : bool, optional
            True - means that reCAPTCHA is invisible. Default: False.
        action : str, optional
            Value of action parameter you found on page. Default: verify.
        minScore : float, only for v3, optional
            The score needed for resolution. Default: 0.7.
        pageAction : str, optional
            Widget action value.
        proxy : str, optional
            Proxy string: type:host:port:user:pass
        page_title : str, optional
            Page title for metadata (improves solving speed)
        """

        # Determine task type based on version and enterprise
        if version == 'v3':
            if enterprise:
                task_type = 'ReCaptchaV3EnterpriseTaskProxyLess'
            else:
                task_type = 'ReCaptchaV3TaskProxyLess'
        else:  # v2
            if enterprise:
                task_type = 'ReCaptchaV2EnterpriseTaskProxyLess'
            else:
                task_type = 'ReCaptchaV2TaskProxyLess'

        task = {
            'type': task_type,
            'websiteURL': url,
            'websiteKey': sitekey,
        }

        # Add optional parameters based on version
        if version == 'v3':
            if 'action' in kwargs:
                task['pageAction'] = kwargs.pop('action')
            if 'minScore' in kwargs:
                task['minScore'] = kwargs.pop('minScore')
        else:  # v2
            invisible = kwargs.pop('invisible', False)
            if invisible:
                task['isInvisible'] = True
            else:
                task['invisible'] = False

            if 'pageAction' in kwargs:
                task['pageAction'] = kwargs.pop('pageAction')

        # Add proxy if provided
        if 'proxy' in kwargs:
            proxy_str = kwargs.pop('proxy')
            # Convert proxy format if needed
            # Expected CapSolver format: type:host:port:user:pass
            task['proxy'] = proxy_str

        # Add metadata for faster solving (CapSolver extension format)
        page_title = kwargs.pop('page_title', None)
        if page_title or url:
            task['metadata'] = {
                'pageURL': url,
                'title': page_title or ''
            }

        # Add enterprisePayload for compatibility
        if version == 'v2':
            task['enterprisePayload'] = kwargs.pop('enterprisePayload', {'s': ''})

        # Add any remaining kwargs to task
        task.update(kwargs)

        result = await self.solve(timeout=self.recaptcha_timeout, task=task)
        return result

    async def image_to_text(self, body, **kwargs):
        """Wrapper for solving image captcha.

        Parameters
        _______________
        body : str
            Base64 encoded image
        module : str, optional
            Specify the module. Default: common
        score : float, optional
            0.8 ~ 1: Highest accuracy, but the request may be answered slower.
        case : bool, optional
            Case sensitive or not
        """

        task = {
            'type': 'ImageToTextTask',
            'body': body,
        }

        # Add optional parameters
        if 'module' in kwargs:
            task['module'] = kwargs.pop('module')
        if 'score' in kwargs:
            task['score'] = kwargs.pop('score')
        if 'case' in kwargs:
            task['case'] = kwargs.pop('case')

        # Add any remaining kwargs
        task.update(kwargs)

        result = await self.solve(timeout=self.default_timeout, task=task)
        return result

    async def normal(self, file, **kwargs):
        """Wrapper for solving normal/image captcha.

        Parameters
        _______________
        file : str
            Can be:
            - Path to the captcha image file on your computer
            - Base64 encoded image (if longer than 50 chars and no dots)
            - URL to the image
        module : str, optional
            Specify the module. Default: common
        score : float, optional
            0.8 ~ 1: Highest accuracy
        case : bool, optional
            Case sensitive or not
        """

        body = await self.get_file_body(file)
        return await self.image_to_text(body, **kwargs)

    async def solve(self, timeout=0, task=None, **kwargs):
        """Sends captcha, receives result.

        Parameters
        __________
        timeout : float
        task : dict
            Task object containing captcha parameters

        Returns
        result : dict
        """

        task_id = await self.create_task(task=task, **kwargs)
        result = {'taskId': task_id}

        timeout = float(timeout or self.default_timeout)
        sleep = self.polling_interval

        solution = await self.wait_result(task_id, timeout, sleep)
        result.update({'code': solution})

        return result

    async def wait_result(self, task_id, timeout, polling_interval):
        max_wait = time.time() + timeout

        while time.time() < max_wait:
            try:
                return await self.get_result(task_id)
            except NetworkException:
                await asyncio.sleep(polling_interval)

        raise TimeoutException(f'timeout {timeout} exceeded')

    async def get_file_body(self, file):
        """Convert file to base64 body"""
        if not file:
            raise ValidationException('File required')

        # If already base64 (no dots and long string)
        if '.' not in file and len(file) > 50:
            return file

        # If URL
        if file.startswith('http'):
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                img_resp = await client.get(file)
                if img_resp.status_code != 200:
                    raise ValidationException(f'File could not be downloaded from url: {file}')
                return b64encode(img_resp.content).decode('utf-8')

        # If file path
        import os
        if not os.path.exists(file):
            raise ValidationException(f'File not found: {file}')

        with open(file, 'rb') as f:
            return b64encode(f.read()).decode('utf-8')

    async def create_task(self, task, **kwargs):
        """Create a task for solving captcha

        Parameters
        _________
        task : dict
            Task object containing type and captcha-specific parameters

        Returns
        task_id : str
        """
        payload = {
            'clientKey': self.API_KEY,
            'task': task,
            'source': 'firefox',  # Mimics CapSolver browser extension for faster solving
            'version': '1.10.5'   # Extension version
        }

        if self.app_id:
            payload['appId'] = self.app_id

        response = await self.api_client.create_task(payload)

        # Check for errors
        if response.get('errorId', 0) != 0:
            error_code = response.get('errorCode', 'UNKNOWN')
            error_desc = response.get('errorDescription', 'Unknown error')
            raise ApiException(f'CapSolver API error: {error_code} - {error_desc}')

        # If synchronous response with solution
        if response.get('status') == 'ready' and 'solution' in response:
            # Return solution directly for sync tasks
            return response['solution']

        # Return task ID for async tasks
        task_id = response.get('taskId')
        if not task_id:
            raise ApiException(f'Cannot get taskId from response: {response}')

        return task_id

    async def get_result(self, task_id):
        """Get the result of a task.

        Parameters
        __________
        task_id : str
            ID of the task sent for solution

        Returns
        solution : str or dict
        """
        payload = {
            'clientKey': self.API_KEY,
            'taskId': task_id,
        }

        response = await self.api_client.get_task_result(payload)

        # Check for errors
        if response.get('errorId', 0) != 0:
            error_code = response.get('errorCode', 'UNKNOWN')
            error_desc = response.get('errorDescription', 'Unknown error')
            raise ApiException(f'CapSolver API error: {error_code} - {error_desc}')

        status = response.get('status')

        if status == 'processing' or status == 'idle':
            raise NetworkException('Task is not ready yet')

        if status != 'ready':
            raise ApiException(f'Unexpected status in response: {status}')

        solution = response.get('solution', {})

        # For recaptcha, extract gRecaptchaResponse
        if 'gRecaptchaResponse' in solution:
            return solution['gRecaptchaResponse']

        # For image captcha, extract text
        if 'text' in solution:
            return solution['text']

        # Return entire solution if no specific field found
        return solution

    async def balance(self):
        """Get account balance

        Returns
        balance : float
        """
        payload = {
            'clientKey': self.API_KEY,
        }

        response = await self.api_client.get_balance(payload)

        # Check for errors
        if response.get('errorId', 0) != 0:
            error_code = response.get('errorCode', 'UNKNOWN')
            error_desc = response.get('errorDescription', 'Unknown error')
            raise ApiException(f'CapSolver API error: {error_code} - {error_desc}')

        balance = response.get('balance', 0)
        return float(balance)
