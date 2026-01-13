"""
Median Blockchain Python SDK

This SDK provides Python bindings for the Median blockchain APIs,
using mospy-wallet for proper Protobuf transaction signing.
"""

__version__ = "1.4.1"
__author__ = "Median Team"
__email__ = "contact@median.network"
__license__ = "Apache-2.0"

import json
import time
import requests
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from mospy import Account, Transaction
from mospy.clients import HTTPClient


class MedianSDKError(Exception):
    """SDK exception for Median-specific errors."""
    pass


@dataclass
class Coin:
    """Represents a coin amount with denomination"""
    denom: str
    amount: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "denom": self.denom,
            "amount": self.amount
        }


class MedianSDK:
    """
    Python SDK for interacting with the Median blockchain.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:1317",
        chain_id: str = "median",
        timeout: int = 30
    ):
        self.api_url = api_url.rstrip('/')
        self.chain_id = chain_id
        self.timeout = timeout
        self.session = requests.Session()
        self._client = HTTPClient(api=self.api_url) # Mospy client

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        raise_on_error: bool = True
    ) -> Dict[str, Any]:
        url = f"{self.api_url}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            if response.status_code >= 400 and raise_on_error:
                try:
                    error_detail = response.json()
                except:
                    error_detail = {"error": response.text}
                raise MedianSDKError(f"HTTP {response.status_code}: {error_detail}")
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            if raise_on_error:
                raise
            return {"error": str(e)}

    # ==================== Account Management ====================

    def create_account(
        self,
        creator_address: str,
        new_account_address: str,
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "creator": creator_address,
            "new_account_address": new_account_address
        }
        return self._broadcast_tx("/median.median.MsgCreateAccount", msg, creator_address, private_key, wait_confirm)

    def get_account(self, address: str) -> Dict[str, Any]:
        endpoint = f"/cosmos/auth/v1beta1/accounts/{address}"
        return self._make_request("GET", endpoint)

    def get_account_balance(self, address: str) -> List[Coin]:
        endpoint = f"/cosmos/bank/v1beta1/balances/{address}"
        response = self._make_request("GET", endpoint)
        balances = response.get("balances", [])
        return [Coin(denom=b["denom"], amount=b["amount"]) for b in balances]

    # ==================== Coin Management ====================

    def mint_coins(
        self,
        authority_address: str,
        recipient_address: str,
        amount: List[Coin],
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "authority": authority_address,
            "recipient": recipient_address,
            "amount": [coin.to_dict() for coin in amount]
        }
        return self._broadcast_tx("/median.median.MsgMintCoins", msg, authority_address, private_key, wait_confirm)

    def burn_coins(
        self,
        authority_address: str,
        amount: List[Coin],
        from_address: str = "",
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "authority": authority_address,
            "from": from_address,
            "amount": [coin.to_dict() for coin in amount]
        }
        return self._broadcast_tx("/median.median.MsgBurnCoins", msg, authority_address, private_key, wait_confirm)

    def transfer_coins(
        self,
        from_address: str,
        to_address: str,
        amount: List[Coin],
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        从指定账户转移代币到目标账户

        参数：
            from_address: 发送方地址
            to_address: 接收方地址
            amount: 代币金额列表
            private_key: 发送方私钥
            wait_confirm: 是否等待交易确认

        返回：
            交易结果字典
        """
        msg = {
            "from_address": from_address,
            "to_address": to_address,
            "amount": [coin.to_dict() for coin in amount]
        }
        return self._broadcast_tx("/cosmos.bank.v1beta1.MsgSend", msg, from_address, private_key, wait_confirm)

    # ==================== Task Management ====================

    def create_task(
        self,
        creator_address: str,
        task_id: str,
        description: str,
        input_data: str,
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "creator": creator_address,
            "task_id": task_id,
            "description": description,
            "input_data": input_data
        }
        return self._broadcast_tx("/median.median.MsgCreateTask", msg, creator_address, private_key, wait_confirm)

    def commit_result(
        self,
        validator_address: str,
        task_id: str,
        result_hash: str,
        nonce: Optional[int] = None,
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        if nonce is None:
             nonce = 0

        msg = {
            "validator": validator_address,
            "task_id": task_id,
            "result_hash": result_hash,
            "nonce": str(nonce)
        }
        return self._broadcast_tx("/median.median.MsgCommitResult", msg, validator_address, private_key, wait_confirm)

    def reveal_result(
        self,
        validator_address: str,
        task_id: str,
        result: Union[int, float, str],
        nonce: Union[int, str],
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "validator": validator_address,
            "task_id": task_id,
            "result": str(result),
            "nonce": str(nonce)
        }
        return self._broadcast_tx("/median.median.MsgRevealResult", msg, validator_address, private_key, wait_confirm)

    # ==================== Query Methods ====================

    def get_task(self, task_id: str) -> Dict[str, Any]:
        endpoint = f"/median/median/task/{task_id}"
        return self._make_request("GET", endpoint)

    def get_consensus_result(self, task_id: str) -> Dict[str, Any]:
        endpoint = f"/median/median/consensus/{task_id}"
        return self._make_request("GET", endpoint)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        endpoint = "/median/median/tasks"
        response = self._make_request("GET", endpoint, raise_on_error=False)
        return response.get("tasks", [])

    def list_commitments(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Query all commitments, optionally filter by task_id"""
        endpoint = "/median/median/commitment"
        response = self._make_request("GET", endpoint, raise_on_error=False)
        if task_id and "commitment" in response:
            response["commitment"] = [c for c in response.get("commitment", []) if c.get("task_id") == task_id]
        return response

    def list_reveals(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Query all reveals, optionally filter by task_id"""
        endpoint = "/median/median/reveal"
        response = self._make_request("GET", endpoint, raise_on_error=False)
        if task_id and "reveal" in response:
            response["reveal"] = [r for r in response.get("reveal", []) if r.get("task_id") == task_id]
        return response

    def list_consensus_results(self) -> Dict[str, Any]:
        """Query all consensus results"""
        endpoint = "/median/median/consensus_result"
        return self._make_request("GET", endpoint, raise_on_error=False)

    # ==================== Blockchain Info ====================

    def get_node_info(self) -> Dict[str, Any]:
        endpoint = "/cosmos/base/tendermint/v1beta1/node_info"
        return self._make_request("GET", endpoint)

    def get_current_height(self) -> int:
        """Query current block height"""
        endpoint = "/cosmos/base/tendermint/v1beta1/blocks/latest"
        result = self._make_request("GET", endpoint, raise_on_error=False)
        return int(result.get("block", {}).get("header", {}).get("height", "0"))

    def get_supply(self, denom: Optional[str] = None) -> Dict[str, Any]:
        if denom:
            endpoint = f"/cosmos/bank/v1beta1/supply/{denom}"
        else:
            endpoint = "/cosmos/bank/v1beta1/supply"
        return self._make_request("GET", endpoint)

    # ==================== Staking Methods ====================

    def delegate_tokens(
        self,
        delegator_address: str,
        validator_address: str,
        amount: List[Coin],
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        质押代币给验证者

        参数：
            delegator_address: 质押者地址
            validator_address: 验证者地址
            amount: 代币金额列表（通常为单个代币）
            private_key: 质押者私钥
            wait_confirm: 是否等待交易确认

        返回：
            交易结果字典
        """
        # 质押通常为单一代币
        if len(amount) != 1:
            raise MedianSDKError("质押金额必须为单个代币类型")

        msg = {
            "delegator_address": delegator_address,
            "validator_address": validator_address,
            "amount": [amount[0].to_dict()]  # 包装在列表中
        }
        return self._broadcast_tx("/cosmos.staking.v1beta1.MsgDelegate", msg, delegator_address, private_key, wait_confirm)

    def undelegate_tokens(
        self,
        delegator_address: str,
        validator_address: str,
        amount: List[Coin],
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        从验证者解押代币

        参数：
            delegator_address: 质押者地址
            validator_address: 验证者地址
            amount: 代币金额列表（通常为单个代币）
            private_key: 质押者私钥
            wait_confirm: 是否等待交易确认

        返回：
            交易结果字典
        """
        # 解押通常为单一代币
        if len(amount) != 1:
            raise MedianSDKError("解押金额必须为单个代币类型")

        msg = {
            "delegator_address": delegator_address,
            "validator_address": validator_address,
            "amount": [amount[0].to_dict()]  # 包装在列表中
        }
        return self._broadcast_tx("/cosmos.staking.v1beta1.MsgUndelegate", msg, delegator_address, private_key, wait_confirm)

    def get_delegation(
        self,
        delegator_address: str,
        validator_address: str
    ) -> Dict[str, Any]:
        """
        查询特定委托信息

        参数：
            delegator_address: 质押者地址
            validator_address: 验证者地址

        返回：
            委托信息字典
        """
        endpoint = f"/cosmos/staking/v1beta1/validators/{validator_address}/delegations/{delegator_address}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_delegator_delegations(
        self,
        delegator_address: str
    ) -> Dict[str, Any]:
        """
        查询质押者的所有委托

        参数：
            delegator_address: 质押者地址

        返回：
            委托列表字典
        """
        endpoint = f"/cosmos/staking/v1beta1/delegations/{delegator_address}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_unbonding_delegations(
        self,
        delegator_address: str,
        validator_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询解押中的委托

        参数：
            delegator_address: 质押者地址
            validator_address: 验证者地址（可选，如果提供则查询特定验证者）

        返回：
            解押中委托列表字典
        """
        if validator_address:
            endpoint = f"/cosmos/staking/v1beta1/delegators/{delegator_address}/unbonding_delegations/{validator_address}"
        else:
            endpoint = f"/cosmos/staking/v1beta1/delegators/{delegator_address}/unbonding_delegations"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_validator_delegations(
        self,
        validator_address: str
    ) -> Dict[str, Any]:
        """
        查询验证者的所有委托

        参数：
            validator_address: 验证者地址

        返回：
            委托列表字典
        """
        endpoint = f"/cosmos/staking/v1beta1/validators/{validator_address}/delegations"
        return self._make_request("GET", endpoint, raise_on_error=False)

    # ==================== NFT Methods ====================

    def get_nft(self, class_id: str, nft_id: str) -> Dict[str, Any]:
        """
        查询特定NFT

        参数：
            class_id: NFT类ID
            nft_id: NFT ID

        返回：
            NFT信息字典
        """
        endpoint = f"/cosmos/nft/v1beta1/nfts/{class_id}/{nft_id}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_nft_class(self, class_id: str) -> Dict[str, Any]:
        """
        查询NFT类信息

        参数：
            class_id: NFT类ID

        返回：
            NFT类信息字典
        """
        endpoint = f"/cosmos/nft/v1beta1/classes/{class_id}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_nft_classes(self) -> Dict[str, Any]:
        """
        查询所有NFT类

        返回：
            NFT类列表字典
        """
        endpoint = "/cosmos/nft/v1beta1/classes"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_nfts_by_owner(self, owner_address: str) -> Dict[str, Any]:
        """
        查询所有者的NFT

        参数：
            owner_address: 所有者地址

        返回：
            NFT列表字典
        """
        endpoint = f"/cosmos/nft/v1beta1/owners/{owner_address}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_nfts_by_class(self, class_id: str) -> Dict[str, Any]:
        """
        查询特定类的所有NFT

        参数：
            class_id: NFT类ID

        返回：
            NFT列表字典
        """
        endpoint = f"/cosmos/nft/v1beta1/nfts/{class_id}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_nft_supply(self, class_id: str) -> Dict[str, Any]:
        """
        查询NFT类的供应量

        参数：
            class_id: NFT类ID

        返回：
            供应量信息字典
        """
        endpoint = f"/cosmos/nft/v1beta1/supply/{class_id}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    # ==================== Certificate Methods ====================

    def issue_staking_certificate(
        self,
        issuer_address: str,
        recipient_address: str,
        stake_amount: Coin,
        validator_address: str,
        certificate_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        发行质押凭证（NFT）

        参数：
            issuer_address: 发行者地址（需要铸造权限）
            recipient_address: 接收者地址
            stake_amount: 质押金额
            validator_address: 验证者地址
            certificate_id: 凭证ID（可选，自动生成）
            metadata: 额外元数据（可选）
            private_key: 发行者私钥
            wait_confirm: 是否等待交易确认

        返回：
            交易结果字典
        """
        # 生成凭证ID
        if certificate_id is None:
            import uuid
            certificate_id = f"cert-{uuid.uuid4().hex[:8]}"

        # 构建凭证元数据
        cert_metadata = {
            "stake_amount": stake_amount.amount,
            "stake_denom": stake_amount.denom,
            "stake_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "validator_address": validator_address,
            "status": "active",
            "redeem_time": None,
            "description": f"质押凭证 - {stake_amount.amount} {stake_amount.denom}"
        }

        if metadata:
            cert_metadata.update(metadata)

        # NFT类ID - 固定为质押凭证类
        class_id = "stake-cert"

        # 准备NFT元数据（JSON字符串）
        nft_metadata = json.dumps(cert_metadata)

        # 构建铸造NFT消息
        msg = {
            "sender": issuer_address,
            "class_id": class_id,
            "id": certificate_id,
            "recipient": recipient_address,
            "uri": nft_metadata  # 将元数据存储在URI字段中
        }

        return self._broadcast_tx("/cosmos.nft.v1beta1.MsgMint", msg, issuer_address, private_key, wait_confirm)

    def redeem_certificate(
        self,
        certificate_id: str,
        owner_address: str,
        class_id: str = "stake-cert",
        burn_on_redeem: bool = True,
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        赎回凭证并作废

        参数：
            certificate_id: 凭证ID
            owner_address: 凭证所有者地址
            class_id: NFT类ID（默认 "stake-cert"）
            burn_on_redeem: 赎回时是否销毁NFT（默认True）
            private_key: 所有者私钥
            wait_confirm: 是否等待交易确认

        返回：
            交易结果字典
        """
        if burn_on_redeem:
            # 销毁NFT
            msg = {
                "sender": owner_address,
                "class_id": class_id,
                "id": certificate_id
            }
            return self._broadcast_tx("/cosmos.nft.v1beta1.MsgBurn", msg, owner_address, private_key, wait_confirm)
        else:
            # 转移NFT到作废地址（例如零地址）
            # 注意：需要先查询当前NFT元数据，更新状态后再转移
            burn_address = "median1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"

            # 先查询NFT当前元数据（验证NFT存在）
            try:
                nft_info = self.get_nft(class_id, certificate_id)
                # 这里可以添加元数据更新逻辑
                _ = nft_info  # 使用变量避免警告
            except:
                pass  # 如果查询失败，继续执行转移

            msg = {
                "sender": owner_address,
                "class_id": class_id,
                "id": certificate_id,
                "recipient": burn_address
            }
            return self._broadcast_tx("/cosmos.nft.v1beta1.MsgSend", msg, owner_address, private_key, wait_confirm)

    def query_certificates(
        self,
        owner_address: str,
        class_id: Optional[str] = "stake-cert",
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        查询用户拥有的凭证

        参数：
            owner_address: 所有者地址
            class_id: NFT类ID（可选，默认 "stake-cert"）
            active_only: 是否只返回活跃凭证（默认True）

        返回：
            凭证列表
        """
        try:
            nfts_response = self.get_nfts_by_owner(owner_address)
            nfts = nfts_response.get("nfts", [])

            certificates = []
            for nft in nfts:
                nft_class_id = nft.get("class_id", "")
                nft_id = nft.get("id", "")

                # 如果指定了class_id，只返回匹配的NFT
                if class_id and nft_class_id != class_id:
                    continue

                # 尝试解析元数据
                uri = nft.get("uri", "{}")
                try:
                    metadata = json.loads(uri)
                except:
                    metadata = {}

                # 如果要求只返回活跃凭证，检查状态
                if active_only:
                    status = metadata.get("status", "active")
                    if status != "active":
                        continue

                certificate = {
                    "certificate_id": nft_id,
                    "class_id": nft_class_id,
                    "owner": owner_address,
                    "metadata": metadata,
                    "nft_info": nft
                }
                certificates.append(certificate)

            return certificates
        except Exception:
            # 如果查询失败，返回空列表
            return []

    def get_certificate(
        self,
        certificate_id: str,
        class_id: str = "stake-cert"
    ) -> Dict[str, Any]:
        """
        查询特定凭证详细信息

        参数：
            certificate_id: 凭证ID
            class_id: NFT类ID（默认 "stake-cert"）

        返回：
            凭证详细信息字典
        """
        try:
            nft_info = self.get_nft(class_id, certificate_id)
            uri = nft_info.get("uri", "{}")

            try:
                metadata = json.loads(uri)
            except:
                metadata = {}

            return {
                "certificate_id": certificate_id,
                "class_id": class_id,
                "owner": nft_info.get("owner", ""),
                "metadata": metadata,
                "nft_info": nft_info
            }
        except Exception as e:
            raise MedianSDKError(f"查询凭证失败: {e}")

    # ==================== Transaction Methods ====================

    def get_tx(self, tx_hash: str) -> Dict[str, Any]:
        """Query transaction by hash"""
        endpoint = f"/cosmos/tx/v1beta1/txs/{tx_hash}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def wait_for_tx(self, tx_hash: str, timeout: int = 30, interval: float = 1.0) -> Dict[str, Any]:
        """
        Wait for transaction to be included in a block.
        Returns transaction details when confirmed.

        Args:
            tx_hash: Transaction hash to wait for
            timeout: Maximum time to wait in seconds (default: 30)
            interval: Polling interval in seconds (default: 1.0)

        Returns:
            Transaction details

        Raises:
            MedianSDKError: If timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                tx = self.get_tx(tx_hash)
                tx_response = tx.get("tx_response", {})
                # If transaction is confirmed (has code field), return result
                if "code" in tx_response:
                    # Check for transaction errors
                    code = tx_response.get("code", 0)
                    if code != 0:
                        error_msg = f"Transaction failed (code={code}): {tx_response.get('raw_log', 'Unknown error')}"
                        raise MedianSDKError(error_msg)
                    return tx
            except MedianSDKError:
                raise
            except Exception:
                # Transaction might still be in mempool, continue waiting
                pass
            time.sleep(interval)
        raise MedianSDKError(f"Transaction confirmation timeout: {tx_hash}")

    # ==================== Distribution (Rewards) Methods ====================

    def get_delegator_rewards(
        self,
        delegator_address: str,
        validator_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询质押奖励

        参数：
            delegator_address: 质押者地址
            validator_address: 验证者地址（可选，如果提供则查询特定验证者的奖励）

        返回：
            奖励信息字典
        """
        if validator_address:
            endpoint = f"/cosmos/distribution/v1beta1/delegators/{delegator_address}/rewards/{validator_address}"
        else:
            endpoint = f"/cosmos/distribution/v1beta1/delegators/{delegator_address}/rewards"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_validator_outstanding_rewards(
        self,
        validator_address: str
    ) -> Dict[str, Any]:
        """
        查询验证者的待分配奖励

        参数：
            validator_address: 验证者地址

        返回：
            待分配奖励信息字典
        """
        endpoint = f"/cosmos/distribution/v1beta1/validators/{validator_address}/outstanding_rewards"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_validator_commission(
        self,
        validator_address: str
    ) -> Dict[str, Any]:
        """
        查询验证者佣金

        参数：
            validator_address: 验证者地址

        返回：
            佣金信息字典
        """
        endpoint = f"/cosmos/distribution/v1beta1/validators/{validator_address}/commission"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_community_pool(self) -> Dict[str, Any]:
        """
        查询社区池余额

        返回：
            社区池余额信息字典
        """
        endpoint = "/cosmos/distribution/v1beta1/community_pool"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def get_distribution_params(self) -> Dict[str, Any]:
        """
        查询分发模块参数

        返回：
            参数信息字典
        """
        endpoint = "/cosmos/distribution/v1beta1/params"
        return self._make_request("GET", endpoint, raise_on_error=False)

    # ==================== Batch Query Methods ====================

    def batch_get_balances(
        self,
        addresses: List[str]
    ) -> Dict[str, List[Coin]]:
        """
        批量查询多个地址的余额

        参数：
            addresses: 地址列表

        返回：
            字典：地址 -> 余额列表
        """
        result = {}
        for address in addresses:
            try:
                balances = self.get_account_balance(address)
                result[address] = balances
            except Exception:
                result[address] = []
        return result

    def batch_get_delegations(
        self,
        delegator_addresses: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量查询多个质押者的委托信息

        参数：
            delegator_addresses: 质押者地址列表

        返回：
            字典：质押者地址 -> 委托信息
        """
        result = {}
        for address in delegator_addresses:
            try:
                delegations = self.get_delegator_delegations(address)
                result[address] = delegations
            except Exception:
                result[address] = {}
        return result

    def batch_get_certificates(
        self,
        owner_addresses: List[str],
        class_id: Optional[str] = "stake-cert",
        active_only: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量查询多个所有者的凭证

        参数：
            owner_addresses: 所有者地址列表
            class_id: NFT类ID（默认 "stake-cert"）
            active_only: 是否只返回活跃凭证（默认True）

        返回：
            字典：所有者地址 -> 凭证列表
        """
        result = {}
        for address in owner_addresses:
            try:
                certificates = self.query_certificates(address, class_id, active_only)
                result[address] = certificates
            except Exception:
                result[address] = []
        return result

    # ==================== Composite Query Methods ====================

    def get_staking_summary(
        self,
        delegator_address: str
    ) -> Dict[str, Any]:
        """
        获取质押综合摘要信息

        包括：
        1. 质押总额
        2. 各个验证者的质押详情
        3. 解押中的质押
        4. 质押奖励
        5. 凭证信息

        参数：
            delegator_address: 质押者地址

        返回：
            综合摘要信息字典
        """
        summary = {
            "delegator_address": delegator_address,
            "total_staked": [],
            "delegations": {},
            "unbonding_delegations": {},
            "rewards": {},
            "certificates": [],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        try:
            # 查询委托信息
            delegations = self.get_delegator_delegations(delegator_address)
            delegation_list = delegations.get("delegation_responses", [])
            summary["delegations"] = delegation_list

            # 计算质押总额
            total_staked = {}
            for delegation in delegation_list:
                balance = delegation.get("balance", {})
                denom = balance.get("denom", "")
                amount = balance.get("amount", "0")
                if denom:
                    total_staked[denom] = total_staked.get(denom, 0) + int(amount)

            summary["total_staked"] = [
                Coin(denom=denom, amount=str(amount))
                for denom, amount in total_staked.items()
            ]

            # 查询解押中的质押
            unbonding = self.get_unbonding_delegations(delegator_address)
            summary["unbonding_delegations"] = unbonding.get("unbonding_responses", [])

            # 查询质押奖励
            rewards = self.get_delegator_rewards(delegator_address)
            summary["rewards"] = rewards

            # 查询凭证
            certificates = self.query_certificates(delegator_address)
            summary["certificates"] = certificates

        except Exception as e:
            summary["error"] = str(e)

        return summary

    def get_validator_summary(
        self,
        validator_address: str
    ) -> Dict[str, Any]:
        """
        获取验证者综合摘要信息

        包括：
        1. 验证者详情
        2. 总委托量
        3. 委托者列表
        4. 待分配奖励
        5. 佣金信息

        参数：
            validator_address: 验证者地址

        返回：
            验证者综合摘要信息字典
        """
        summary = {
            "validator_address": validator_address,
            "delegations": {},
            "total_delegated": [],
            "outstanding_rewards": {},
            "commission": {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        try:
            # 查询验证者委托
            delegations = self.get_validator_delegations(validator_address)
            summary["delegations"] = delegations

            # 计算总委托量
            delegation_responses = delegations.get("delegation_responses", [])
            total_delegated = {}
            for delegation in delegation_responses:
                balance = delegation.get("balance", {})
                denom = balance.get("denom", "")
                amount = balance.get("amount", "0")
                if denom:
                    total_delegated[denom] = total_delegated.get(denom, 0) + int(amount)

            summary["total_delegated"] = [
                Coin(denom=denom, amount=str(amount))
                for denom, amount in total_delegated.items()
            ]

            # 查询待分配奖励
            outstanding_rewards = self.get_validator_outstanding_rewards(validator_address)
            summary["outstanding_rewards"] = outstanding_rewards

            # 查询佣金
            commission = self.get_validator_commission(validator_address)
            summary["commission"] = commission

        except Exception as e:
            summary["error"] = str(e)

        return summary

    # ==================== Utility Methods ====================

    def _check_tx_result(self, result: Dict[str, Any]) -> None:
        """
        Check transaction result, raise exception if failed.
        Provides helpful messages for sequence mismatch errors.
        """
        code = result.get("code", 0)
        if code != 0:
            codespace = result.get("codespace", "")
            raw_log = result.get("raw_log", "")
            error_msg = f"Transaction failed (code={code}, codespace={codespace}): {raw_log}"

            # Check for sequence error
            if "sequence" in raw_log.lower() or code == 32:
                error_msg += "\nHint: This may be an account sequence mismatch."
                error_msg += "\nPossible causes:"
                error_msg += "\n1. Previous transaction still in mempool"
                error_msg += "\n2. Account sequence number cache expired"
                error_msg += "\nSuggestion: Wait a few seconds and retry, or query latest account sequence"

            raise MedianSDKError(error_msg)

    def _broadcast_tx(
        self,
        msg_type: str,
        msg_content: Dict[str, Any],
        sender_address: str,
        private_key: Optional[Union[str, bytes]] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Broadcast a signed transaction using mospy.
        Optionally wait for transaction confirmation.
        """
        if not private_key:
            raise ValueError("Private key is required for signing transactions")

        # Handle private key conversion
        try:
            if isinstance(private_key, bytes):
                pk_bytes = private_key
            elif isinstance(private_key, str):
                # Remove 0x prefix if present
                clean_key = private_key.replace("0x", "")
                pk_bytes = bytes.fromhex(clean_key)
            else:
                raise ValueError(f"Unsupported private key type: {type(private_key)}")
        except Exception as e:
             raise ValueError(f"Invalid private key format: {e}")

        # Create account instance
        hrp = sender_address.split('1')[0]

        account = Account(
            private_key=pk_bytes.hex(),
            hrp=hrp,
            protobuf="cosmos"
        )

        # Sync account info (sequence, account number) from chain
        acc_info = self.get_account(sender_address)
        base_acc = acc_info.get("account", {})
        # Handle nesting
        if "base_vesting_account" in base_acc:
            base_acc = base_acc["base_vesting_account"]["base_account"]

        account_number = int(base_acc.get("account_number", 0))
        sequence = int(base_acc.get("sequence", 0))

        account.account_number = account_number
        account.next_sequence = sequence

        # Create Transaction
        tx = Transaction(
            account=account,
            chain_id=self.chain_id,
            gas=200000
        )

        # Set fee (required for mospy 0.6.0)
        # Using stake denom as it's the base denom for gas fees
        # Minimum fee is 5000 stake as per blockchain requirements
        tx.set_fee(amount=5000, denom="stake")

        # Add Message
        tx.add_dict_msg(msg_content, msg_type)

        # Get transaction bytes
        # Try get_tx_bytes_base64 first, fallback to get_tx_bytes + base64 encode
        if hasattr(tx, 'get_tx_bytes_base64'):
            tx_bytes_base64 = tx.get_tx_bytes_base64()
        else:
            tx_bytes = tx.get_tx_bytes()
            tx_bytes_base64 = base64.b64encode(tx_bytes).decode('utf-8')

        payload = {
            "tx_bytes": tx_bytes_base64,
            "mode": "BROADCAST_MODE_SYNC"
        }

        endpoint = "/cosmos/tx/v1beta1/txs"
        result = self._make_request("POST", endpoint, data=payload)

        # Extract tx_hash from response
        tx_response = result.get("tx_response", {})
        tx_hash = tx_response.get("txhash", "")

        # Check for immediate failures
        self._check_tx_result(tx_response)

        # If wait_confirm is True, wait for transaction to be included
        if wait_confirm and tx_hash:
            try:
                confirmed_tx = self.wait_for_tx(tx_hash, timeout=30)
                confirmed_response = confirmed_tx.get("tx_response", {})
                self._check_tx_result(confirmed_response)
                return {"txhash": tx_hash, "confirmed": True, **confirmed_response}
            except MedianSDKError:
                # Return original result if wait fails
                return result

        return result


def create_sdk(
    api_url: str = "http://localhost:1317",
    chain_id: str = "median"
) -> MedianSDK:
    return MedianSDK(api_url=api_url, chain_id=chain_id)
