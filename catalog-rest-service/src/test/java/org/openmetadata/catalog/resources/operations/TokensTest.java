/*
 *  Copyright 2021 Collate
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  http://www.apache.org/licenses/LICENSE-2.0
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

package org.openmetadata.catalog.resources.operations;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.openmetadata.catalog.fernet.Fernet.FERNET_PREFIX;
import static org.openmetadata.catalog.util.TestUtils.ADMIN_AUTH_HEADERS;
import static org.openmetadata.catalog.util.TestUtils.readResponse;

import java.io.IOException;
import java.util.Map;
import javax.ws.rs.client.Entity;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.Status;
import org.apache.http.client.HttpResponseException;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.openmetadata.catalog.CatalogApplicationTest;
import org.openmetadata.catalog.fernet.Fernet;
import org.openmetadata.catalog.security.SecurityUtil;

public class TokensTest extends CatalogApplicationTest {

  @BeforeAll
  static void setup() {
    Fernet.getInstance().setFernetKey("ihZpp5gmmDvVsgoOG6OVivKWwC9vd5JQ");
  }

  @Test
  void post_tokens_200_OK() throws IOException {
    String secret = "secret";
    String token = encrypt(secret, ADMIN_AUTH_HEADERS);
    assertNotEquals(token, secret);
    assertTrue(token.startsWith(FERNET_PREFIX));
    assertEquals(secret, decrypt(token, ADMIN_AUTH_HEADERS));
  }

  public static String encrypt(String token, Map<String, String> headers) throws HttpResponseException {
    WebTarget target = getOperationsResource("tokens/encrypt");
    return post(target, token, String.class, headers);
  }

  public static String decrypt(String token, Map<String, String> headers) throws HttpResponseException {
    WebTarget target = getOperationsResource("tokens/decrypt");
    return post(target, token, String.class, headers);
  }

  public static <T, K> T post(WebTarget target, K request, Class<T> clz, Map<String, String> headers)
      throws HttpResponseException {
    Response response =
        SecurityUtil.addHeaders(target, headers).post(Entity.entity(request, MediaType.TEXT_PLAIN_TYPE));
    return readResponse(response, clz, Status.OK.getStatusCode());
  }
}
