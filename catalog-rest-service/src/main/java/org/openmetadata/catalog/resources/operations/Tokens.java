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

import io.swagger.annotations.Api;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import javax.ws.rs.Consumes;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.SecurityContext;
import javax.ws.rs.core.UriInfo;
import lombok.extern.slf4j.Slf4j;
import org.openmetadata.catalog.fernet.Fernet;
import org.openmetadata.catalog.jdbi3.CollectionDAO;
import org.openmetadata.catalog.resources.Collection;
import org.openmetadata.catalog.security.Authorizer;
import org.openmetadata.catalog.security.SecurityUtil;

@Slf4j
@Path("/operations/v1/tokens")
@Api(value = "Tokens", tags = "Tokens")
@Produces(MediaType.TEXT_PLAIN)
@Consumes(MediaType.TEXT_PLAIN)
@Collection(name = "tokens")
public class Tokens {
  private final Authorizer authorizer;
  private final Fernet fernet;

  public Tokens(CollectionDAO dao, Authorizer authorizer) {
    fernet = Fernet.getInstance();
    this.authorizer = authorizer;
  }

  @POST
  @Path("/decrypt")
  @Operation(
      summary = "Decrypt a token",
      tags = "tokens",
      description = "Tokens API to decrypt tokens with the OpenMetadata Fernet key.",
      responses = {
        @ApiResponse(responseCode = "200", description = "Decrypt a token"),
        @ApiResponse(responseCode = "400", description = "Bad request")
      })
  public Response decrypt(@Context UriInfo uriInfo, @Context SecurityContext securityContext, String token) {
    SecurityUtil.checkAdminOrBotRole(authorizer, securityContext);
    return Response.status(Response.Status.OK).entity(fernet.decrypt(token)).build();
  }

  @POST
  @Path("/encrypt")
  @Operation(
      summary = "Encrypt a secret",
      tags = "tokens",
      description = "Tokens API to encrypt secrets with the OpenMetadata Fernet key.",
      responses = {
        @ApiResponse(responseCode = "200", description = "Encrypt a secret"),
        @ApiResponse(responseCode = "400", description = "Bad request")
      })
  public Response encrypt(@Context UriInfo uriInfo, @Context SecurityContext securityContext, String secret) {
    return Response.status(Response.Status.OK).entity(fernet.encrypt(secret)).build();
  }
}
