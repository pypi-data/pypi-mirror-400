#!/usr/bin/env python3

import httpx
import logging

logger = logging.getLogger(__name__)


class AsyncApiClient:
    def __init__(self, base_url='https://api.capsolver.com', verify_ssl=True):
        self.base_url = base_url
        self.verify_ssl = verify_ssl

    async def _request(self, endpoint: str, data: dict) -> dict:
        """
        Make async HTTP POST request to CapSolver API

        :param endpoint: API endpoint (e.g., '/createTask', '/getTaskResult')
        :param data: Request payload
        :return: JSON response
        """
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            logger.debug(f"Making request to {endpoint} with data: {data}")
            response = await client.post(
                f'{self.base_url}{endpoint}',
                json=data,
                timeout=30.0
            )

            # Try to get error details before raising
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    logger.error(f"CapSolver API error response: {error_data}")
                    raise Exception(f"CapSolver API error: {error_data}")
                except Exception as e:
                    if "CapSolver API error" in str(e):
                        raise
                    pass

            response.raise_for_status()
            return response.json()

    async def create_task(self, data: dict) -> dict:
        """Create a task for solving captcha"""
        return await self._request('/createTask', data)

    async def get_task_result(self, data: dict) -> dict:
        """Get the result of a task"""
        return await self._request('/getTaskResult', data)

    async def get_balance(self, data: dict) -> dict:
        """Get account balance"""
        return await self._request('/getBalance', data)
